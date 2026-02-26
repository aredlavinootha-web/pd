"""
Plagiarism detection using tree-sitter for Java.
Compares AST structure similarity between code snippets.
"""

import difflib

try:
    from tree_sitter import Parser, Language, Node
    from tree_sitter_java import language as java_language
    JAVA_LANGUAGE = Language(java_language())
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False
    JAVA_LANGUAGE = None


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
    """Parse Java code and return serialized AST string."""
    if not TREE_SITTER_AVAILABLE:
        return ""
    parser = Parser()
    parser.language = JAVA_LANGUAGE
    tree = parser.parse(bytes(code, "utf8"))
    return _ast_to_string(tree.root_node, bytes(code, "utf8"))


def compare_code_treesitter_java(
    main_student_id: str,
    main_code: str,
    other_students: list[dict],
) -> dict:
    """
    Compare main student code with all other students using tree-sitter (Java).

    Args:
        main_student_id: ID of the main student
        main_code: Code content of the main student
        other_students: List of dicts with keys 'id' and 'code'

    Returns:
        Response dict with tool name and comparison results
    """
    if not TREE_SITTER_AVAILABLE:
        return {
            "tool": "treesitter_java",
            "available": False,
            "error": "tree-sitter-java not installed. Run: pip install tree-sitter tree-sitter-java",
            "results": [],
        }

    try:
        main_ast = _parse_and_serialize(main_code)
    except Exception as e:
        return {
            "tool": "treesitter_java",
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
        "tool": "treesitter_java",
        "available": True,
        "main_student_id": main_student_id,
        "results": results,
    }
