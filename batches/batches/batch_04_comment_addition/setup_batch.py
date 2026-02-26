"""
Boilerplate setup script for Batch 4: Comment Addition
Loads ref.py and compare.py and prepares them for similarity analysis.
"""

import os


def load_code_file(filepath):
    """Load and return file contents as string."""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def setup_batch():
    """Load both code files from this batch directory."""
    batch_dir = os.path.dirname(os.path.abspath(__file__))
    ref_path = os.path.join(batch_dir, "ref.py")
    compare_path = os.path.join(batch_dir, "compare.py")
    return {
        "ref": load_code_file(ref_path),
        "compare": load_code_file(compare_path),
        "batch_name": "04_comment_addition_removal",
        "expected_cheating": True,
        "expected_similarity_range": (85, 100),
    }
