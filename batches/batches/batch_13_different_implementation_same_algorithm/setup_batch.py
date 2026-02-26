"""
Setup for Batch 13: Different Implementation Same Algorithm (NOT cheating)
"""

import os


def load_code_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def setup_batch():
    batch_dir = os.path.dirname(os.path.abspath(__file__))
    return {
        "ref": load_code_file(os.path.join(batch_dir, "ref.py")),
        "compare": load_code_file(os.path.join(batch_dir, "compare.py")),
        "batch_name": "13_different_implementation_same_algorithm",
        "expected_cheating": False,
        "expected_similarity_range": (55, 90),
    }
