"""
Plagiarism detection using tree-sitter for C++.
Compares AST structure similarity between code snippets.
"""

import difflib

try:
    from tree_sitter import Parser, Language, Node
    from tree_sitter_cpp import language as cpp_language
    CPP_LANGUAGE = Language(cpp_language())
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False
    CPP_LANGUAGE = None


def _ast_to_string(node: "Node", source: bytes) -> str:
    """Serialize AST node to string representation (DFS of node types)."""
    parts = []
    if node.type:
        parts.append(node.type)
    for i in range(node.child_count):
        child = node.child(i)
        parts.append(_ast_to_string(child, source))
    return " ".join(parts)


def _parse_and_serialize(code: str) -> str:
    """Parse C++ code and return serialized AST string."""
    if not TREE_SITTER_AVAILABLE:
        return ""
    parser = Parser()
    parser.language = CPP_LANGUAGE
    tree = parser.parse(bytes(code, "utf8"))
    return _ast_to_string(tree.root_node, bytes(code, "utf8"))


def compare_code_treesitter_cpp(
    main_student_id: str,
    main_code: str,
    other_students: list[dict],
) -> dict:
    """
    Compare main student code with all other students using tree-sitter (C++).

    Args:
        main_student_id: ID of the main student
        main_code: Code content of the main student
        other_students: List of dicts with keys 'id' and 'code'

    Returns:
        Response dict with tool name and comparison results
    """
    if not TREE_SITTER_AVAILABLE:
        return {
            "tool": "treesitter_cpp",
            "available": False,
            "error": "tree-sitter packages not installed. Run: pip install tree-sitter tree-sitter-cpp",
            "results": [],
        }

    try:
        main_ast = _parse_and_serialize(main_code)
    except Exception as e:
        return {
            "tool": "treesitter_cpp",
            "available": True,
            "main_student_id": main_student_id,
            "error": f"Failed to parse main code: {e}",
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
                "ast_similarity": 0.0,
                "error": "Empty code content",
            })
            continue

        try:
            other_ast = _parse_and_serialize(other_code)
        except Exception as e:
            results.append({
                "other_student_id": other_id,
                "similarity": 0.0,
                "ast_similarity": 0.0,
                "error": str(e),
            })
            continue

        if not main_ast or not other_ast:
            results.append({
                "other_student_id": other_id,
                "similarity": 0.0,
                "ast_similarity": 0.0,
            })
            continue

        matcher = difflib.SequenceMatcher(None, main_ast, other_ast)
        ast_similarity = matcher.ratio()

        results.append({
            "other_student_id": other_id,
            "similarity": round(ast_similarity, 4),
            "ast_similarity": round(ast_similarity, 4),
        })

    return {
        "tool": "treesitter_cpp",
        "available": True,
        "main_student_id": main_student_id,
        "results": results,
    }


def detect(
    current_submission: dict,
    past_submissions: list[dict],
    threshold: float = 0.85,
) -> dict:
    """
    Detect plagiarism using tree-sitter (C++). Returns expected response format.

    Args:
        current_submission: { "student_id", "submission_id", "code" }
        past_submissions: List of { "student_id", "submission_id", "code" }
        threshold: Minimum similarity to count as match (default 0.85)

    Returns:
        { "matches_found": bool, "threshold_used": float, "matches": [...] }
    """
    if not TREE_SITTER_AVAILABLE:
        return {"matches_found": False, "threshold_used": threshold, "matches": []}

    main_code = current_submission.get("code", "")
    main_id = current_submission.get("student_id", "")

    other_students = [
        {"id": p.get("student_id", ""), "code": p.get("code", "")}
        for p in past_submissions
    ]

    raw = compare_code_treesitter_cpp(main_id, main_code, other_students)
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
