"""
Plagiarism detection using tree-sitter for Python.
Compares AST structure similarity between code snippets.
"""

import difflib
import re

try:
    from tree_sitter import Parser, Language, Node
    from tree_sitter_python import language as python_language
    PY_LANGUAGE = Language(python_language())
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False
    PY_LANGUAGE = None


def _get_node_text(node: "Node", source: bytes) -> str:
    """Get source text for a node."""
    if node.start_byte < node.end_byte:
        return source[node.start_byte:node.end_byte].decode("utf-8", errors="replace")
    return ""


def _ast_to_string(node: "Node", source: bytes, include_semantic: bool = True) -> str:
    """
    Serialize AST node to string representation (DFS of node types).
    When include_semantic=True, adds:
    - Attribute method names (upper vs lower) for template/skeleton distinction
    - Comparison operators (>, <=) for minor logic distinction
    - Assignment targets for code reordering distinction
    """
    parts = []
    if node.type:
        parts.append(node.type)

    # Include semantic details for better accuracy on specific cases
    if include_semantic:
        if node.type == "attribute":
            # Include method name (e.g., upper vs lower) for template/skeleton
            for i in range(node.child_count):
                child = node.child(i)
                if child.type == "identifier" and i > 0:
                    text = _get_node_text(child, source)
                    if text:
                        parts.append(f"attr:{text}")
                        break
        elif node.type == "comparison_operator":
            # Include operator (>, <=, etc.) for minor logic modification
            for i in range(node.child_count):
                child = node.child(i)
                if child.type in (">", "<", ">=", "<=", "==", "!="):
                    parts.append(f"op:{child.type}")
                    break

    for i in range(node.child_count):
        child = node.child(i)
        parts.append(_ast_to_string(child, source, include_semantic))
    return " ".join(parts)


def _parse_and_serialize(code: str) -> str:
    """Parse Python code and return serialized AST string."""
    if not TREE_SITTER_AVAILABLE:
        return ""
    parser = Parser()
    parser.language = PY_LANGUAGE
    tree = parser.parse(bytes(code, "utf8"))
    return _ast_to_string(tree.root_node, bytes(code, "utf8"))


def compare_code_treesitter_python(
    main_student_id: str,
    main_code: str,
    other_students: list[dict],
) -> dict:
    """
    Compare main student code with all other students using tree-sitter (Python).

    Args:
        main_student_id: ID of the main student
        main_code: Code content of the main student
        other_students: List of dicts with keys 'id' and 'code'

    Returns:
        Response dict with tool name and comparison results
    """
    if not TREE_SITTER_AVAILABLE:
        return {
            "tool": "treesitter_python",
            "available": False,
            "error": "tree-sitter packages not installed. Run: pip install tree-sitter tree-sitter-python",
            "results": [],
        }

    try:
        main_ast = _parse_and_serialize(main_code)
    except Exception as e:
        return {
            "tool": "treesitter_python",
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

        results.append({
            "other_student_id": other_id,
            "similarity": round(ast_similarity, 4),
            "ast_similarity": round(ast_similarity, 4),
        })

    return {
        "tool": "treesitter_python",
        "available": True,
        "main_student_id": main_student_id,
        "results": results,
    }
