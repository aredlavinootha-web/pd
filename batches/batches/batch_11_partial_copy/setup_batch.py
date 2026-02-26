"""
Setup for Batch 11: Partial Copy (CHEATING)
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
        "batch_name": "11_partial_copy",
        "expected_cheating": True,
        "expected_similarity_range": (50, 75),
        "strip_skeleton": True,
    }
