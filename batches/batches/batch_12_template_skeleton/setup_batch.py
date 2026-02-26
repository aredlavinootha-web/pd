"""
Setup for Batch 12: Template/Skeleton Similarity (NOT cheating)
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
        "batch_name": "12_template_skeleton",
        "expected_cheating": False,
        "expected_similarity_range": (20, 45),
        "strip_skeleton": True,
    }
