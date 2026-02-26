"""
Setup for Batch 10: Code Reordering (CHEATING)
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
        "batch_name": "10_code_reordering",
        "expected_cheating": True,
        "expected_similarity_range": (75, 95),
    }
