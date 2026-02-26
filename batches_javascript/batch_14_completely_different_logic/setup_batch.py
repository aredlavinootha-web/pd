import os
def load(p): return open(p, "r", encoding="utf-8").read()
def setup_batch():
    d = os.path.dirname(os.path.abspath(__file__))
    return {"ref": load(os.path.join(d, "ref.js")), "compare": load(os.path.join(d, "compare.js")),
            "batch_name": "14_completely_different_logic", "expected_cheating": False, "expected_similarity_range": (10, 35)}
