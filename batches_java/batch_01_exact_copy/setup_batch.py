import os
def load(p): return open(p, "r", encoding="utf-8").read()
def setup_batch():
    d = os.path.dirname(os.path.abspath(__file__))
    return {"ref": load(os.path.join(d, "ref.java")), "compare": load(os.path.join(d, "compare.java")),
            "batch_name": "01_exact_copy", "expected_cheating": True, "expected_similarity_range": (95, 100)}
