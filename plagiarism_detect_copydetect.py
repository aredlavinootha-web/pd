"""
Plagiarism detection using copydetect (winnowing algorithm).
Compares main student code against other students' code.
"""

import io

try:
    import copydetect
except ImportError:
    copydetect = None


def _get_file_extension(language: str) -> str:
    """Map language to file extension for copydetect tokenizer."""
    lang_map = {"python": "py", "cpp": "cpp", "c": "c", "java": "java", "javascript": "js", "csharp": "cs"}
    return lang_map.get(language.lower(), "py")


def compare_code_copydetect(
    main_student_id: str,
    main_code: str,
    other_students: list[dict],
    language: str = "python",
    k: int = 10,
    win_size: int = 1,
) -> dict:
    """
    Compare main student code with all other students using copydetect.

    Args:
        main_student_id: ID of the main student
        main_code: Code content of the main student
        other_students: List of dicts with keys 'id' and 'code'
        language: Programming language (python, cpp, etc.)
        k: K-gram length for fingerprinting
        win_size: Window size for winnowing

    Returns:
        Response dict with tool name and comparison results
    """
    if copydetect is None:
        return {
            "tool": "copydetect",
            "available": False,
            "error": "copydetect package not installed. Run: pip install copydetect",
            "results": [],
        }

    ext = _get_file_extension(language)
    main_filename = f"main.{ext}"

    try:
        main_fp = copydetect.CodeFingerprint(
            main_filename, k, win_size, filter=True, language=language, fp=io.StringIO(main_code)
        )
    except Exception as e:
        return {
            "tool": "copydetect",
            "available": True,
            "error": str(e),
            "results": [],
        }

    results = []
    for other in other_students:
        other_id = other.get("id", "unknown")
        other_code = other.get("code", "")

        if not other_code.strip():
            results.append({
                "other_student_id": other_id,
                "similarity": 0.0,
                "similarity_main": 0.0,
                "similarity_other": 0.0,
                "token_overlap": 0,
                "error": "Empty code content",
            })
            continue

        try:
            other_filename = f"{other_id}.{ext}"
            other_fp = copydetect.CodeFingerprint(
                other_filename, k, win_size, filter=True, language=language, fp=io.StringIO(other_code)
            )
            token_overlap, similarities, slices = copydetect.compare_files(main_fp, other_fp)

            sim_main, sim_other = similarities[0], similarities[1]
            avg_similarity = (sim_main + sim_other) / 2 if (sim_main or sim_other) else 0.0

            results.append({
                "other_student_id": other_id,
                "similarity": round(avg_similarity, 4),
                "similarity_main": round(sim_main, 4),
                "similarity_other": round(sim_other, 4),
                "token_overlap": int(token_overlap),
                "slices_main": slices[0].tolist() if hasattr(slices[0], "tolist") else list(slices[0]),
                "slices_other": slices[1].tolist() if hasattr(slices[1], "tolist") else list(slices[1]),
            })
        except Exception as e:
            results.append({
                "other_student_id": other_id,
                "similarity": 0.0,
                "similarity_main": 0.0,
                "similarity_other": 0.0,
                "token_overlap": 0,
                "error": str(e),
            })

    return {
        "tool": "copydetect",
        "available": True,
        "main_student_id": main_student_id,
        "results": results,
    }
