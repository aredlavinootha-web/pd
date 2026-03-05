"""
Plagiarism detection using copydetect (winnowing algorithm).
Compares main student code against other students' code.

JavaScript: Pygments uses Token.Name.Other for JS identifiers; copydetect only
normalizes Name, Name.Variable, Name.Attribute, so variable/function renames
gave low similarity. We patch utils.filter_code and detector.filter_code to
treat Name.Other as V when language is javascript/js.
"""

import io

try:
    import copydetect
except ImportError:
    copydetect = None

# JavaScript: Pygments uses Name.Other for JS identifiers; copydetect only normalizes
# Name, Name.Variable, Name.Attribute — so JS variable/function names stay literal.
# Patch utils.filter_code and detector.filter_code (detector caches it at import).
if copydetect is not None:
    from pygments import lexers, token
    import pygments.util
    import numpy as np
    import copydetect.utils as _cd_utils
    import copydetect.detector as _cd_detector
    _orig_filter = _cd_utils.filter_code

    def _filter_js(code, filename, language=None):
        if language not in ("javascript", "js"):
            return _orig_filter(code, filename, language)
        try:
            lexer = lexers.get_lexer_by_name(language)
            tokens = lexer.get_tokens(code)
        except pygments.util.ClassNotFound:
            return _orig_filter(code, filename, language)
        out_code, offset, offsets = "", 0, [[0, 0]]
        vt = {token.Name, token.Name.Variable, token.Name.Attribute, token.Name.Other}
        for t in tokens:
            if t[0] in vt:
                out_code += "V"
                offsets.append([len(out_code) - 1, offset])
                offset += len(t[1]) - 1
            elif t[0] in token.Name.Function:
                out_code += "F"
                offsets.append([len(out_code) - 1, offset])
                offset += len(t[1]) - 1
            elif t[0] in token.Name.Class:
                out_code += "O"
                offsets.append([len(out_code) - 1, len(t[1]) - 1])
                offset += len(t[1]) - 1
            elif t[0] == token.Comment.Preproc or t[0] == token.Comment.Hashbang:
                out_code += "P"
                offsets.append([len(out_code) - 1, offset])
                offset += len(t[1]) - 1
            elif t[0] in token.Text or t[0] in token.Comment:
                offsets.append([len(out_code) - 1, offset])
                offset += len(t[1])
            elif t[0] in token.Literal.String:
                if t[1] in ("'", '"'):
                    out_code += '"'
                else:
                    out_code += "S"
                    offsets.append([len(out_code) - 1, offset])
                    offset += len(t[1]) - 1
            else:
                out_code += t[1]
        return out_code, np.array(offsets)

    _cd_utils.filter_code = _filter_js
    _cd_detector.filter_code = _filter_js


def _get_file_extension(language: str) -> str:
    """Map language to file extension for copydetect tokenizer."""
    lang_map = {"python": "py", "cpp": "cpp", "c": "c", "java": "java", "javascript": "js", "csharp": "cs"}
    return lang_map.get(language.lower(), "py")


def compare_code_copydetect(
    main_student_id: str,
    main_code: str,
    other_students: list[dict],
    language: str = "python",
    k: int = 8,
    win_size: int = 1,
    boilerplate_code: str | None = None,
) -> dict:
    """
    Compare main student code with all other students using copydetect.

    Args:
        main_student_id: ID of the main student
        main_code: Code content of the main student
        other_students: List of dicts with keys 'id' and 'code'
        language: Programming language (python, cpp, etc.)
        k: K-gram length for fingerprinting (default 8; smaller improves function extraction)
        win_size: Window size for winnowing
        boilerplate_code: Optional code to exclude as boilerplate (e.g., template/skeleton)

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

    boilerplate_hashes = []
    if boilerplate_code and boilerplate_code.strip():
        try:
            bp_fp = copydetect.CodeFingerprint(
                f"boilerplate.{ext}", k, win_size, filter=True, language=language,
                fp=io.StringIO(boilerplate_code.strip()),
            )
            boilerplate_hashes = list(getattr(bp_fp, "hashes", []))
        except Exception:
            pass

    try:
        main_fp = copydetect.CodeFingerprint(
            main_filename, k, win_size, filter=True, language=language, fp=io.StringIO(main_code),
            boilerplate=boilerplate_hashes,
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
                other_filename, k, win_size, filter=True, language=language, fp=io.StringIO(other_code),
                boilerplate=boilerplate_hashes,
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


def compare_all_pairs_copydetect(
    students: list[dict],
    language: str = "python",
    k: int = 8,
    win_size: int = 1,
    top_n: int | None = None,
) -> dict:
    """
    Compare every student with every other student using copydetect.

    Args:
        students: List of dicts with keys 'id' and 'code'
        language: Programming language
        k: K-gram length for fingerprinting
        win_size: Window size for winnowing
        top_n: If set, include top N matches per student in the response

    Returns:
        {
            "available": bool,
            "pairs": [{ "student_a", "student_b", "similarity", ... }],
            "comparisons_count": int,
            "students_count": int,
            "top_matches_per_student": { student_id: [...] } (if top_n set)
        }
    """
    if copydetect is None:
        return {
            "available": False,
            "error": "copydetect package not installed. Run: pip install copydetect",
            "pairs": [],
            "comparisons_count": 0,
            "students_count": len(students),
        }

    ext = _get_file_extension(language)

    fingerprints: dict[str, object] = {}
    for student in students:
        sid = student.get("id", "unknown")
        code = student.get("code", "")
        if not code.strip():
            continue
        try:
            fp = copydetect.CodeFingerprint(
                f"{sid}.{ext}", k, win_size, filter=True, language=language,
                fp=io.StringIO(code),
            )
            fingerprints[sid] = fp
        except Exception:
            continue

    ids = list(fingerprints.keys())
    pairs: list[dict] = []

    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            sid_a, sid_b = ids[i], ids[j]
            try:
                token_overlap, similarities, slices = copydetect.compare_files(
                    fingerprints[sid_a], fingerprints[sid_b],
                )
                sim_a, sim_b = similarities[0], similarities[1]
                avg_sim = (sim_a + sim_b) / 2 if (sim_a or sim_b) else 0.0
                pairs.append({
                    "student_a": sid_a,
                    "student_b": sid_b,
                    "similarity": round(avg_sim, 4),
                    "similarity_a": round(sim_a, 4),
                    "similarity_b": round(sim_b, 4),
                    "token_overlap": int(token_overlap),
                })
            except Exception:
                pairs.append({
                    "student_a": sid_a,
                    "student_b": sid_b,
                    "similarity": 0.0,
                    "similarity_a": 0.0,
                    "similarity_b": 0.0,
                    "token_overlap": 0,
                })

    pairs.sort(key=lambda p: p["similarity"], reverse=True)

    result: dict = {
        "available": True,
        "pairs": pairs,
        "comparisons_count": len(pairs),
        "students_count": len(students),
    }

    if top_n is not None and top_n > 0:
        top_matches: dict[str, list] = {sid: [] for sid in ids}
        for p in pairs:
            a, b = p["student_a"], p["student_b"]
            if len(top_matches[a]) < top_n:
                top_matches[a].append({"matched_id": b, "similarity": p["similarity"]})
            if len(top_matches[b]) < top_n:
                top_matches[b].append({"matched_id": a, "similarity": p["similarity"]})
        result["top_matches_per_student"] = top_matches

    return result
