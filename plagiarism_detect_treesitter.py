"""
Plagiarism detection using tree-sitter (Python or C++).
Dispatches to treesitter_python or treesitter_cpp based on language.
"""

from plagiarism_detect_treesitter_python import compare_code_treesitter_python
from plagiarism_detect_treesitter_cpp import compare_code_treesitter_cpp


def detect(
    current_submission: dict,
    past_submissions: list[dict],
    language: str = "python",
    threshold: float = 0.85,
) -> dict:
    """
    Detect plagiarism using tree-sitter. Returns expected response format.
    Uses treesitter_python for Python, treesitter_cpp for C++.

    Args:
        current_submission: { "student_id", "submission_id", "code" }
        past_submissions: List of { "student_id", "submission_id", "code" }
        language: "python" or "cpp"
        threshold: Minimum similarity to count as match (default 0.85)

    Returns:
        { "matches_found": bool, "threshold_used": float, "matches": [...] }
    """
    main_code = current_submission.get("code", "")
    main_id = current_submission.get("student_id", "")

    other_students = [
        {"id": p.get("student_id", ""), "code": p.get("code", "")}
        for p in past_submissions
    ]

    if language.lower() == "cpp":
        raw = compare_code_treesitter_cpp(main_id, main_code, other_students)
    else:
        raw = compare_code_treesitter_python(main_id, main_code, other_students)

    if not raw.get("available") or "error" in raw:
        return {"matches_found": False, "threshold_used": threshold, "matches": []}

    matches = []
    for r in raw.get("results", []):
        sim = r.get("similarity", 0)
        if sim >= threshold:
            other = next((p for p in past_submissions if p.get("student_id") == r.get("other_student_id")), {})
            matches.append({
                "matched_student_id": r.get("other_student_id", ""),
                "matched_submission_id": other.get("submission_id", ""),
                "similarity_score": round(sim, 4),
                "matched_code": other.get("code", ""),
            })

    return {
        "matches_found": len(matches) > 0,
        "threshold_used": threshold,
        "matches": matches,
    }
