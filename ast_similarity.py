"""
Shared AST similarity using Jaccard n-gram overlap.
Used by all tree-sitter plagiarism detectors instead of difflib.SequenceMatcher.
"""

DEFAULT_N = 4


def get_ngrams(ast_string: str, n: int = DEFAULT_N) -> set:
    """Extract n-grams (contiguous token tuples) from tokenized AST string."""
    tokens = ast_string.split()
    if len(tokens) < n:
        return set()
    return set(tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1))


def compute_jaccard_similarity(
    main_ast: str,
    other_ast: str,
    n: int = DEFAULT_N,
) -> float:
    """
    Jaccard similarity between two AST strings: |intersection| / |union| of n-gram sets.
    Order-independent; efficient for reordered/partial copies.
    """
    if not main_ast or not other_ast:
        return 0.0
    set1 = get_ngrams(main_ast, n=n)
    set2 = get_ngrams(other_ast, n=n)
    if not set1 and not set2:
        return 1.0
    if not set1 or not set2:
        return 0.0
    inter = len(set1 & set2)
    union = len(set1 | set2)
    return inter / union if union else 0.0
