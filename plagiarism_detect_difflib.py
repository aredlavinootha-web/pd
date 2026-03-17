"""
Plagiarism detection using difflib SequenceMatcher.
Uses Ratcliff-Obershelp algorithm for sequence similarity.

For long code (> ~1500 chars), ratio() can be O(n²) or worse and cause timeouts.
We use quick_ratio() only when either string exceeds MAX_CHARS_FOR_FULL_RATIO.
"""

import difflib

# Above this length, SequenceMatcher.ratio() is too slow (O(n²)+); use quick_ratio() only
MAX_CHARS_FOR_FULL_RATIO = 1500


def compare_code_difflib(
    main_student_id: str,
    main_code: str,
    other_students: list[dict],
) -> dict:
    """
    Compare main student code with all other students using difflib.

    Args:
        main_student_id: ID of the main student
        main_code: Code content of the main student
        other_students: List of dicts with keys 'id' and 'code'

    Returns:
        Response dict with tool name and comparison results
    """
    results = []
    main_lines = main_code.splitlines()
    main_normalized = "\n".join(line.strip() for line in main_lines if line.strip())

    for other in other_students:
        other_id = other.get("id", "unknown")
        other_code = other.get("code", "")

        if not other_code.strip():
            results.append({
                "other_student_id": other_id,
                "similarity": 0.0,
                "ratio": 0.0,
                "quick_ratio": 0.0,
                "error": "Empty code content",
            })
            continue

        other_lines = other_code.splitlines()
        other_normalized = "\n".join(line.strip() for line in other_lines if line.strip())

        if not main_normalized or not other_normalized:
            results.append({
                "other_student_id": other_id,
                "similarity": 0.0,
                "ratio": 0.0,
                "quick_ratio": 0.0,
            })
            continue

        use_fast_path = len(main_code) > MAX_CHARS_FOR_FULL_RATIO or len(other_code) > MAX_CHARS_FOR_FULL_RATIO
        if use_fast_path:
            # ratio() is O(n²) or worse on long strings → timeout. Use quick_ratio() only (upper bound, fast).
            matcher = difflib.SequenceMatcher(None, main_code, other_code)
            quick_ratio = matcher.quick_ratio()
            matcher_norm = difflib.SequenceMatcher(None, main_normalized, other_normalized)
            quick_norm = matcher_norm.quick_ratio()
            ratio = quick_ratio
            ratio_normalized = quick_norm
        else:
            matcher = difflib.SequenceMatcher(None, main_code, other_code)
            ratio = matcher.ratio()
            quick_ratio = matcher.quick_ratio()
            matcher_normalized = difflib.SequenceMatcher(None, main_normalized, other_normalized)
            ratio_normalized = matcher_normalized.ratio()

        results.append({
            "other_student_id": other_id,
            "similarity": round(ratio, 4),
            "ratio": round(ratio, 4),
            "quick_ratio": round(quick_ratio, 4),
            "ratio_normalized": round(ratio_normalized, 4),
        })

    return {
        "tool": "difflib",
        "available": True,
        "main_student_id": main_student_id,
        "results": results,
    }
