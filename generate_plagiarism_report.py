"""
Plagiarism Report Generator Script

Generates a comprehensive CSV report for multiple questions across different languages.
Follows the exact same logic as the /check API endpoint.

For each question → language → student, computes:
- Copydetect similarity (%)
- Tree-sitter AST Jaccard similarity (%)
- Semantic embedding similarity (%)
- Overall weighted plagiarism score (%)

Outputs CSV with top 5 matches per student including both codes.

Key parity with /check API:
- Embedding similarities fetched from Pinecone via vector query (top_k=N), exactly
  like find_similar_submissions() — scores are server-side calibrated cosine values.
- Tool comparisons use pre-computed all-pairs matrices (copydetect + tree-sitter).
- Scoring weights: copydetect=0.50, treesitter=0.25, embeddings=0.25.
- Structural penalty pre-computed once per student (cached), not re-run per pair.
"""

import csv
import time
import logging
import concurrent.futures
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import vector_db
import code_normalizer
from plagiarism_detect_copydetect import compare_all_pairs_copydetect
from plagiarism_detect_treesitter_python import compare_code_treesitter_python
from plagiarism_detect_treesitter_cpp import compare_code_treesitter_cpp
from plagiarism_detect_treesitter_java import compare_code_treesitter_java
from plagiarism_detect_treesitter_c import compare_code_treesitter_c
from plagiarism_detect_treesitter_csharp import compare_code_treesitter_csharp
from plagiarism_detect_treesitter_javascript import compare_code_treesitter_javascript

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# ── Configuration ─────────────────────────────────────────────────────────────
EXAM_ID = "coding_contest_1"
QUESTION_IDS = [
    "01cbe553-12d5-470d-b18b-c2af36f243a2",
    "488d0034-555f-4b8e-a1d0-707f1b9cc4a1",
    "2145f5f1-72b0-4546-b7fc-3760b00963f7",
    "c2710019-1810-4e2b-b83f-b89e82ddf8d7",
]

TOP_MATCHES = 5
SIMILARITY_THRESHOLD = 0.75

# Scoring weights — must match scoring_engine.WEIGHTS exactly
_W_EMB = 0.25
_W_CD  = 0.50
_W_TS  = 0.25

# Pinecone: parallel workers for embedding queries
_EMB_QUERY_WORKERS = 20

# Tree-sitter tool map keyed by resolved language
TREESITTER_TOOL_MAP = {
    "python":   compare_code_treesitter_python,
    "python39": compare_code_treesitter_python,
    "python3":  compare_code_treesitter_python,
    "cpp":      compare_code_treesitter_cpp,
    "c":        compare_code_treesitter_c,
    "java":     compare_code_treesitter_java,
    "javascript": compare_code_treesitter_javascript,
    "js":       compare_code_treesitter_javascript,
    "csharp":   compare_code_treesitter_csharp,
}


# ── Pinecone embedding similarity matrix ─────────────────────────────────────
def _query_pinecone_for_student(
    student_id: str,
    submission_id: str,
    question_id: str,
    exam_id: str,
    top_k: int,
    pinecone_filter: dict,
) -> Tuple[str, Dict[str, float]]:
    """
    Fetch the student's stored embedding then query Pinecone with top_k=N.
    Returns (student_id, {other_student_id: calibrated_similarity}).

    Mirrors find_similar_submissions() in vector_db.py exactly:
      - Same filter (type=submission, questionId, examId)
      - Same _calibrate_score() applied to raw Pinecone cosine scores
    """
    embedding = vector_db.get_submission_embedding(submission_id)
    if not embedding:
        return student_id, {}

    response = vector_db._index.query(
        vector=embedding,
        top_k=top_k,
        filter=pinecone_filter,
        include_metadata=True,
    )

    scores: Dict[str, float] = {}
    for match in response.get("matches", []):
        other_sid = match["metadata"].get("studentId", "")
        if other_sid and other_sid != student_id:
            calibrated = vector_db._calibrate_score(match["score"])
            scores[other_sid] = calibrated

    return student_id, scores


def precompute_embedding_similarities(
    all_submissions: List[dict],
    question_id: str,
    exam_id: str,
) -> Dict[str, Dict[str, float]]:
    """
    Query Pinecone for every student using their stored embedding.
    top_k = N (total students), so we get back the full similarity list.

    Runs all queries in parallel (20 workers) — much faster than sequential.
    Returns {student_id: {other_student_id: calibrated_similarity}}.
    """
    n = len(all_submissions)
    logger.info(f"Querying Pinecone embeddings for {n} students (top_k={n}, {_EMB_QUERY_WORKERS} workers)...")
    t0 = time.time()

    pinecone_filter: dict = {
        "type":       {"$eq": "submission"},
        "questionId": {"$eq": question_id},
    }
    normalized_exam_id = str(exam_id).strip() if exam_id and str(exam_id).strip() else None
    if normalized_exam_id:
        pinecone_filter["examId"] = {"$eq": normalized_exam_id}

    sim_matrix: Dict[str, Dict[str, float]] = {sub["student_id"]: {} for sub in all_submissions}

    with concurrent.futures.ThreadPoolExecutor(max_workers=_EMB_QUERY_WORKERS) as executor:
        futures = {
            executor.submit(
                _query_pinecone_for_student,
                sub["student_id"],
                sub["id"],           # submission_id used to fetch the stored embedding
                question_id,
                exam_id,
                n,                   # top_k = total students in this group
                pinecone_filter,
            ): sub["student_id"]
            for sub in all_submissions
        }

        completed = 0
        for future in concurrent.futures.as_completed(futures):
            try:
                student_id, scores = future.result()
                sim_matrix[student_id] = scores
            except Exception as e:
                student_id = futures[future]
                logger.debug(f"Embedding query failed for {student_id}: {e}")
            completed += 1
            if completed % 50 == 0 or completed == n:
                logger.info(f"  Embedding queries: {completed}/{n}")

    # Log coverage stats
    covered = sum(1 for scores in sim_matrix.values() if scores)
    logger.info(
        f"Embedding matrix done: {covered}/{n} students have scores, "
        f"elapsed={time.time()-t0:.1f}s"
    )
    return sim_matrix


# ── Structural penalty (cached per student) ───────────────────────────────────
def _penalty_from_func_diff(func_diff: int) -> float:
    """Map function count difference → penalty factor (matches calculate_structural_penalty)."""
    if func_diff >= 3:
        return 0.3
    if func_diff == 2:
        return 0.5
    if func_diff == 1:
        return 0.75
    return 1.0


def precompute_struct_stats(submissions: List[dict], language: str) -> Dict[str, dict]:
    """
    Run analyze_structure() once per student and cache.
    Avoids running O(N²) regex calls inside the scoring loop.
    """
    cache = {}
    for sub in submissions:
        try:
            cache[sub["student_id"]] = code_normalizer.analyze_structure(
                sub["code"], language
            )
        except Exception:
            cache[sub["student_id"]] = {"functions": 0}
    logger.info(f"Struct stats cached for {len(cache)} students")
    return cache


# ── Inline overall score ──────────────────────────────────────────────────────
def _compute_overall_score(
    emb_score: float,
    cd_score: float,
    ts_score: float,
    cd_available: bool,
    ts_available: bool,
    struct_a: dict,
    struct_b: dict,
) -> float:
    """
    Inline replica of scoring_engine.calculate_weighted_score.
    Weights: embeddings=0.25, copydetect=0.50, treesitter=0.25.
    Structural penalty from cached function count diff.
    """
    weighted_sum = emb_score * _W_EMB
    total_weight = _W_EMB  # embeddings always "available" (0.0 when no match)

    if cd_available:
        weighted_sum += cd_score * _W_CD
        total_weight += _W_CD

    if ts_available:
        weighted_sum += ts_score * _W_TS
        total_weight += _W_TS

    if total_weight == 0:
        return 0.0

    score = weighted_sum / total_weight

    func_diff = abs(struct_a.get("functions", 0) - struct_b.get("functions", 0))
    score *= _penalty_from_func_diff(func_diff)

    return max(0.0, min(1.0, score))


# ── Pre-compute all-pairs tool matrices ──────────────────────────────────────
def precompute_all_pairs_tools(
    all_submissions: List[dict],
    language: str,
) -> Tuple[dict, dict]:
    """
    Compute copydetect (native all-pairs) + tree-sitter (O(N²/2)) in parallel threads.
    Returns:
        copydetect_matrix: {(student_a, student_b): similarity}  — both directions
        treesitter_matrix: same
    """
    n = len(all_submissions)
    lang = code_normalizer.resolve_language(language)
    submissions_for_tools = [
        {"id": sub["student_id"], "code": sub["code"]}
        for sub in all_submissions
    ]

    def run_copydetect():
        t0 = time.time()
        matrix = {}
        try:
            cd_result = compare_all_pairs_copydetect(submissions_for_tools, language)
            if cd_result.get("available") and cd_result.get("pairs"):
                for pair in cd_result["pairs"]:
                    a, b = pair["student_a"], pair["student_b"]
                    sim = pair.get("similarity", 0.0)
                    matrix[(a, b)] = sim
                    matrix[(b, a)] = sim
            logger.info(
                f"Copydetect all-pairs: {len(matrix)//2} pairs in {time.time()-t0:.1f}s"
            )
        except Exception as e:
            logger.error(f"Copydetect all-pairs failed: {e}")
        return matrix

    def run_treesitter():
        t0 = time.time()
        matrix = {}
        treesitter_func = TREESITTER_TOOL_MAP.get(lang)
        if not treesitter_func:
            logger.warning(f"No tree-sitter support for language: {lang}")
            return matrix
        try:
            for i, sub_i in enumerate(all_submissions):
                if (i + 1) % 50 == 0:
                    logger.info(f"  Tree-sitter progress: {i+1}/{n}")
                sid_i = sub_i["student_id"]
                code_i = sub_i["code"]
                others = [
                    {"id": sub["student_id"], "code": sub["code"]}
                    for sub in all_submissions[i + 1:]
                ]
                if not others:
                    continue
                ts_result = treesitter_func(sid_i, code_i, others)
                if ts_result.get("available") and ts_result.get("results"):
                    for r in ts_result["results"]:
                        other_id = r["other_student_id"]
                        sim = r.get("similarity", 0.0)
                        matrix[(sid_i, other_id)] = sim
                        matrix[(other_id, sid_i)] = sim
            logger.info(
                f"Tree-sitter all-pairs: {len(matrix)//2} pairs in {time.time()-t0:.1f}s"
            )
        except Exception as e:
            logger.error(f"Tree-sitter all-pairs failed: {e}")
        return matrix

    # Run both tools in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        fut_cd = executor.submit(run_copydetect)
        fut_ts = executor.submit(run_treesitter)
        copydetect_matrix = fut_cd.result()
        treesitter_matrix = fut_ts.result()

    logger.info(
        f"Tool pre-computation done — "
        f"CD: {len(copydetect_matrix)//2} pairs, TS: {len(treesitter_matrix)//2} pairs"
    )
    return copydetect_matrix, treesitter_matrix


# ── Per-student top-N matches ─────────────────────────────────────────────────
def get_top_matches_for_student(
    student_id: str,
    other_submissions: List[dict],
    student_struct: dict,
    embedding_sim_matrix: Dict[str, Dict[str, float]],
    struct_cache: Dict[str, dict],
    copydetect_matrix: dict,
    treesitter_matrix: dict,
) -> List[dict]:
    """
    Score one student against all others using pre-computed matrices.
    Embedding similarity comes from Pinecone query results (calibrated).
    """
    student_emb_scores = embedding_sim_matrix.get(student_id, {})
    results = []

    for other_sub in other_submissions:
        other_id = other_sub["student_id"]
        other_code = other_sub["code"]

        # Embedding: from Pinecone query result (calibrated, same as /check API)
        emb_score = student_emb_scores.get(other_id, 0.0)

        # Tool scores from pre-computed matrices
        cd_available = (student_id, other_id) in copydetect_matrix
        ts_available = (student_id, other_id) in treesitter_matrix
        cd_score = copydetect_matrix.get((student_id, other_id), 0.0)
        ts_score = treesitter_matrix.get((student_id, other_id), 0.0)

        # Overall score (structural penalty from cached struct stats)
        other_struct = struct_cache.get(other_id, {"functions": 0})
        overall_score = _compute_overall_score(
            emb_score, cd_score, ts_score,
            cd_available, ts_available,
            student_struct, other_struct,
        )

        results.append({
            "matched_student_id": other_id,
            "embeddings_score":   emb_score,
            "copydetect_score":   cd_score,
            "treesitter_score":   ts_score,
            "overall_score":      overall_score,
            "matched_code":       other_code,
        })

    results.sort(key=lambda x: x["overall_score"], reverse=True)
    return results[:TOP_MATCHES]


# ── Main ─────────────────────────────────────────────────────────────────────
def generate_report():
    """Generate plagiarism report CSV."""
    start_time = time.time()
    logger.info("=" * 80)
    logger.info("Starting Plagiarism Report Generation")
    logger.info(f"Exam ID: {EXAM_ID}  |  Questions: {len(QUESTION_IDS)}")
    logger.info("=" * 80)

    if not vector_db.initialize_index():
        logger.error("Failed to initialize Pinecone. Exiting.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"plagiarism_report_{EXAM_ID}_{timestamp}.csv"

    csv_headers = [
        "question_id", "language", "student_id", "matched_student_id",
        "cd %", "ast %", "embeddings %", "overall_plag_score",
        "student_code", "matched_student_code",
    ]
    rows = []

    for question_id in QUESTION_IDS:
        logger.info(f"\n{'='*80}\nProcessing Question: {question_id}\n{'='*80}")

        try:
            all_submissions = vector_db.get_submissions_by_question(question_id, EXAM_ID)
            
        except Exception as e:
            logger.error(f"Failed to load submissions for {question_id}: {e}")
            continue

        if not all_submissions:
            logger.warning(f"No submissions for {question_id}. Skipping.")
            continue

        logger.info(f"Loaded {len(all_submissions)} submissions")

        # Group by language
        by_lang: Dict[str, List[dict]] = {}
        for sub in all_submissions:
            lang = (sub.get("language") or "python").strip().lower()
            by_lang.setdefault(lang, []).append(sub)

        logger.info(f"Languages: {list(by_lang.keys())}")

        for language, lang_subs in by_lang.items():
            n = len(lang_subs)
            logger.info(f"\n{'-'*60}\nLanguage: {language} ({n} students)\n{'-'*60}")

            if n < 2:
                logger.warning(f"Need ≥2 students for {language}, got {n}. Skipping.")
                continue

            # Step 1: Pre-compute tool matrices (CD + TS) in parallel
            t0 = time.time()
            copydetect_matrix, treesitter_matrix = precompute_all_pairs_tools(
                lang_subs, language
            )
            logger.info(f"Tool matrices: {time.time()-t0:.1f}s")

            # Step 2: Pre-compute structural stats once per student
            struct_cache = precompute_struct_stats(lang_subs, language)

            # Step 3: Pinecone embedding queries — parallel, top_k=N per student
            # Each student's stored embedding queries against all N students.
            # Calibrated scores returned by Pinecone (same as /check API flow).
            embedding_sim_matrix = precompute_embedding_similarities(
                lang_subs, question_id, EXAM_ID
            )

            # Step 4: Score every student vs every other → top 5
            for idx, submission in enumerate(lang_subs, 1):
                student_id = submission["student_id"]
                student_code = submission["code"]

                if idx % 100 == 0 or idx == 1:
                    logger.info(f"Scoring student {idx}/{n}")

                if not student_code or not student_code.strip():
                    logger.warning(f"Empty code for {student_id}. Skipping.")
                    continue

                other_subs = [s for s in lang_subs if s["student_id"] != student_id]
                student_struct = struct_cache.get(student_id, {"functions": 0})

                try:
                    top_matches = get_top_matches_for_student(
                        student_id,
                        other_subs,
                        student_struct,
                        embedding_sim_matrix,
                        struct_cache,
                        copydetect_matrix,
                        treesitter_matrix,
                    )
                    for match in top_matches:
                        rows.append({
                            "question_id":          question_id,
                            "language":             language,
                            "student_id":           student_id,
                            "matched_student_id":   match["matched_student_id"],
                            "cd %":                 round(match["copydetect_score"] * 100, 2),
                            "ast %":                round(match["treesitter_score"] * 100, 2),
                            "embeddings %":         round(match["embeddings_score"] * 100, 2),
                            "overall_plag_score":   round(match["overall_score"] * 100, 2),
                            "student_code":         student_code,
                            "matched_student_code": match["matched_code"],
                        })
                except Exception as e:
                    logger.error(f"Error for student {student_id}: {e}", exc_info=True)

    # Write CSV
    rows.sort(key=lambda r: (r["student_id"], r["question_id"], r["language"]))
    logger.info(f"\n{'='*80}\nWriting {len(rows)} rows → {output_filename}\n{'='*80}")
    with open(output_filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=csv_headers)
        writer.writeheader()
        writer.writerows(rows)

    elapsed = time.time() - start_time
    logger.info(f"Done in {elapsed:.1f}s | Output: {output_filename}")


if __name__ == "__main__":
    try:
        generate_report()
    except KeyboardInterrupt:
        logger.info("Interrupted by user.")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
