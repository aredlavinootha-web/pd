"""
Measure computation time for plagiarism detection using AST comparison (tree-sitter Python).
100 student submissions, pairwise comparison, top 10 matches per student.

Optional: set memory limit (e.g. 2 GB) with env var MAX_MEMORY_MB=2048 (Linux/Unix only).
"""

import os
import sys
import time

# Ensure project root is on path
sys.path.insert(0, ".")

# Optional memory limit (must be set before heavy imports). Linux/Unix only.
_max_mb = os.environ.get("MAX_MEMORY_MB")
if _max_mb:
    try:
        import resource
        _limit_bytes = int(_max_mb) * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (_limit_bytes, _limit_bytes))
        print(f"[Memory limit: {_max_mb} MB]\n")
    except (ValueError, OSError, ImportError) as e:
        print(f"Warning: could not set memory limit ({_max_mb} MB): {e}\n")

from generate_student_codes import generate_student_submissions
from plagiarism_detect_treesitter_python import _parse_and_serialize
import difflib
import re

NUM_STUDENTS = 100
TOP_N = 10


def compute_ast_similarity(main_ast: str, other_ast: str) -> float:
    """
    Compute similarity between two AST strings.
    Extracts the sequence matching and blending logic.
    """
    if not main_ast or not other_ast:
        return 0.0

    # Structural similarity (LCS) - good for same structure, order-flexible
    matcher = difflib.SequenceMatcher(None, main_ast, other_ast)
    structural_sim = matcher.ratio()

    # Order-sensitive component: only apply when structural is very high (>0.92)
    # to penalize code reordering without hurting function extraction / partial copy
    main_tokens = main_ast.split()
    other_tokens = other_ast.split()
    n = min(len(main_tokens), len(other_tokens))
    order_matches = sum(1 for i in range(n) if main_tokens[i] == other_tokens[i]) if n else 0
    order_sim = order_matches / n if n else 0.0

    if structural_sim > 0.92:
        # Likely reordering: blend in order-sensitivity to reduce inflated score
        ast_similarity = 0.85 * structural_sim + 0.15 * order_sim
    else:
        ast_similarity = structural_sim

    # Template/skeleton: same boilerplate, different logic (e.g., upper vs lower)
    # Cap similarity when core logic differs (attr: method names differ)
    main_attrs = set(re.findall(r"attr:\w+", main_ast))
    other_attrs = set(re.findall(r"attr:\w+", other_ast))
    if main_attrs and other_attrs and main_attrs != other_attrs and structural_sim > 0.95:
        ast_similarity = min(ast_similarity, 0.85)

    return round(ast_similarity, 4)


def main():
    print(f"Generating {NUM_STUDENTS} Python student submissions...")
    students = generate_student_submissions(n=NUM_STUDENTS)
    print(f"Generated {len(students)} submissions.\n")

    print("Pre-parsing codes to AST strings...")
    start_parse = time.perf_counter()
    
    # 1. Pre-parse AST strings once per code
    for student in students:
        code = student.get("code", "")
        if not code.strip():
            student["ast"] = ""
            continue
        try:
            student["ast"] = _parse_and_serialize(code)
        except Exception as e:
            student["ast"] = ""
            
    parse_elapsed = time.perf_counter() - start_parse
    print(f"Parsed {len(students)} files in {parse_elapsed:.3f} seconds.\n")

    print(f"Running pairwise AST comparison ({NUM_STUDENTS} students)...")
    start_compare = time.perf_counter()

    # 2. Pairwise comparison caching symmetric (i, j) calculations
    similarity_cache = {}
    top_matches_per_student = {}
    
    for i, student in enumerate(students):
        main_id = student["id"]
        main_ast = student.get("ast", "")
        
        results = []
        for j, other in enumerate(students):
            if i == j:
                continue
            
            other_id = other["id"]
            other_ast = other.get("ast", "")
            
            # Use cached similarity if computed earlier, since metric is essentially symmetric
            pair_key = tuple(sorted([main_id, other_id]))
            if pair_key in similarity_cache:
                sim = similarity_cache[pair_key]
            else:
                sim = compute_ast_similarity(main_ast, other_ast)
                similarity_cache[pair_key] = sim
                
            results.append({
                "other_student_id": other_id,
                "similarity": sim
            })
            
        results.sort(key=lambda r: r.get("similarity", 0.0), reverse=True)
        top_matches_per_student[main_id] = results[:TOP_N]

    compare_elapsed = time.perf_counter() - start_compare
    total_elapsed = parse_elapsed + compare_elapsed

    total_pairs = NUM_STUDENTS * (NUM_STUDENTS - 1) // 2
    print(f"Comparisons: {total_pairs}, Students: {NUM_STUDENTS}\n")

    print("=" * 70)
    print("TOP 10 MATCHES PER STUDENT (AST / tree-sitter - Optimized)")
    print("=" * 70)
    for sid in sorted(top_matches_per_student.keys(), key=lambda x: int(x.split("_")[1])):
        matches = top_matches_per_student[sid]
        print(f"\n{sid}:")
        for rank, m in enumerate(matches, 1):
            other_id = m["other_student_id"]
            sim = m["similarity"]
            pct = sim * 100
            print(f"  {rank:2}. {other_id}  {pct:6.2f}%")

    print("\n" + "=" * 70)
    print(f"TOTAL COMPUTATION TIME (Optimized): {total_elapsed:.3f} seconds")
    print(f" - Parsing time  : {parse_elapsed:.3f}s")
    print(f" - Compare time  : {compare_elapsed:.3f}s")
    print("=" * 70)


if __name__ == "__main__":
    main()
