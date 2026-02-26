import os
def load(p): return open(p, "r", encoding="utf-8").read()
def setup_batch():
    d = os.path.dirname(os.path.abspath(__file__))
    return {"ref": load(os.path.join(d, "ref.js")), "compare": load(os.path.join(d, "compare.js")),
            "batch_name": "05_function_extraction", "expected_cheating": True, "expected_similarity_range": (55, 85)}
