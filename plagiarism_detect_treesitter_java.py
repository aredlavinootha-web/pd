"""
Plagiarism detection using tree-sitter for Java.
Compares AST structure similarity between code snippets.
"""

import difflib
import re

try:
    from tree_sitter import Parser, Language, Node
    from tree_sitter_java import language as java_language
    JAVA_LANGUAGE = Language(java_language())
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False
    JAVA_LANGUAGE = None

# Loop node types - include kind to distinguish for vs while vs enhanced-for
LOOP_NODE_KINDS = {
    "for_statement": "loop:for",
    "while_statement": "loop:while",
    "do_statement": "loop:do",
    "enhanced_for_statement": "loop:foreach",
}


def _get_node_text(node: "Node", source: bytes) -> str:
    """Get source text for a node."""
    if node.start_byte < node.end_byte:
        return source[node.start_byte:node.end_byte].decode("utf-8", errors="replace")
    return ""


def _ast_to_string(node: "Node", source: bytes, include_semantic: bool = True) -> str:
    """
    Serialize AST node to string representation (DFS of node types).
    When include_semantic=True, adds:
    - Loop kind (for vs while vs foreach) to distinguish loop type changes
    - Binary operator (>, <=) for minor logic distinction
    - Method name (toUpperCase vs toLowerCase) for template distinction
    """
    parts = []
    if node.type:
        if node.type in LOOP_NODE_KINDS:
            parts.append(LOOP_NODE_KINDS[node.type])
        else:
            parts.append(node.type)

    if include_semantic:
        if node.type == "binary_expression":
            for i in range(node.child_count):
                child = node.child(i)
                if child.type in (">", "<", ">=", "<=", "==", "!=", "+", "-", "*", "/", "%"):
                    parts.append(f"op:{child.type}")
                    break
        elif node.type == "method_invocation":
            # Include method name: "method(args)" has method at i=0; "obj.method()" at i=2
            for i in range(node.child_count):
                child = node.child(i)
                if child.type == "identifier":
                    text = _get_node_text(child, source)
                    if text and (i == 0 and (node.child_count < 2 or node.child(1).type != ".") or (i >= 2 and node.child(1).type == ".")):
                        parts.append(f"method:{text}")
                        break

    for i in range(node.child_count):
        child = node.child(i)
        parts.append(_ast_to_string(child, source, include_semantic))
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

        # Structural similarity (LCS)
        matcher = difflib.SequenceMatcher(None, main_ast, other_ast)
        structural_sim = matcher.ratio()

        # Bag-of-nodes: when order differs (reordering, partial copy)
        main_tokens = main_ast.split()
        other_tokens = other_ast.split()
        main_set = set(main_tokens)
        other_set = set(other_tokens)
        set_overlap = len(main_set & other_set) / len(main_set | other_set) if (main_set | other_set) else 0.0

        if set_overlap >= 0.99:
            # Same node set, different order (whitespace, code reordering)
            ast_similarity = 0.4 * structural_sim + 0.6 * set_overlap
        elif structural_sim < 0.5 and set_overlap >= 0.8:
            ast_similarity = structural_sim
        elif structural_sim < 0.5 and set_overlap > 0.6 and structural_sim >= 0.35:
            ast_similarity = 0.4 * structural_sim + 0.6 * set_overlap
        elif structural_sim >= 0.35 and structural_sim < 0.75 and set_overlap > 0.45 and set_overlap < 0.95:
            ast_similarity = 0.55 * structural_sim + 0.45 * set_overlap
        else:
            ast_similarity = structural_sim

        # Template/skeleton: cap when method names differ (toUpperCase vs toLowerCase)
        main_methods = set(re.findall(r"method:\w+", main_ast))
        other_methods = set(re.findall(r"method:\w+", other_ast))
        if main_methods and other_methods and main_methods != other_methods and structural_sim > 0.95:
            ast_similarity = min(ast_similarity, 0.85)

        # Minor logic: cap when comparison operators differ
        main_ops = set(re.findall(r"op:[<>=!]+", main_ast))
        other_ops = set(re.findall(r"op:[<>=!]+", other_ast))
        if main_ops and other_ops and main_ops != other_ops and structural_sim > 0.95:
            ast_similarity = min(ast_similarity, 0.90)

        # Loop type: when loop kinds differ, cap to expected range
        main_loops = set(re.findall(r"loop:\w+", main_ast))
        other_loops = set(re.findall(r"loop:\w+", other_ast))
        if main_loops and other_loops and main_loops != other_loops and structural_sim > 0.75:
            ast_similarity = min(ast_similarity, 0.65)

        # Recursive vs iterative: when loop/call counts differ significantly
        main_loop_cnt = (
            main_tokens.count("loop:for") + main_tokens.count("loop:while")
            + main_tokens.count("loop:do") + main_tokens.count("loop:foreach")
        )
        other_loop_cnt = (
            other_tokens.count("loop:for") + other_tokens.count("loop:while")
            + other_tokens.count("loop:do") + other_tokens.count("loop:foreach")
        )
        main_method_cnt = len(re.findall(r"method:\w+", main_ast))
        other_method_cnt = len(re.findall(r"method:\w+", other_ast))
        if structural_sim > 0.5 and abs(main_loop_cnt - other_loop_cnt) >= 1 and abs(main_method_cnt - other_method_cnt) >= 1:
            ast_similarity = min(ast_similarity, 0.50)

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
