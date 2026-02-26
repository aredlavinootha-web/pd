import os
def load(p): return open(p, "r", encoding="utf-8").read()
def setup_batch():
    d = os.path.dirname(os.path.abspath(__file__))
    return {"ref": load(os.path.join(d, "ref.cpp")), "compare": load(os.path.join(d, "compare.cpp")),
            "batch_name": "07_recursive_iterative", "expected_cheating": False, "expected_similarity_range": (25, 50)}
