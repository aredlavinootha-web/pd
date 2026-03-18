"""
Shared AST similarity using Jaccard n-gram overlap.
Used by all tree-sitter plagiarism detectors instead of difflib.SequenceMatcher.
No hard limit on code length: for very long ASTs we sample n-grams to keep runtime bounded.
"""

import random

DEFAULT_N = 4
# Max n-grams per AST to avoid O(tokens) set size on huge files; sampling keeps Jaccard stable
MAX_NGRAMS = 12000
# AST token count above which we sample n-grams (avoids huge sets for long code)
SAMPLING_TOKEN_THRESHOLD = 8000


def get_ngrams(ast_string: str, n: int = DEFAULT_N) -> set:
    """Extract n-grams (contiguous token tuples) from tokenized AST string.
    For long ASTs (many tokens), sample up to MAX_NGRAMS n-grams so runtime stays bounded."""
    tokens = ast_string.split()
    if len(tokens) < n:
        return set()
    num_ngrams = len(tokens) - n + 1
    if num_ngrams <= MAX_NGRAMS:
        return set(tuple(tokens[i : i + n]) for i in range(num_ngrams))
    indices = random.Random(42).sample(range(num_ngrams), MAX_NGRAMS)
    return set(tuple(tokens[i : i + n]) for i in indices)


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
