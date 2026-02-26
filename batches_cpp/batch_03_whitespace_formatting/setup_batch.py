import os
def load(p): return open(p, "r", encoding="utf-8").read()
def setup_batch():
    d = os.path.dirname(os.path.abspath(__file__))
    return {"ref": load(os.path.join(d, "ref.cpp")), "compare": load(os.path.join(d, "compare.cpp")),
            "batch_name": "03_whitespace_formatting", "expected_cheating": True, "expected_similarity_range": (90, 100)}
