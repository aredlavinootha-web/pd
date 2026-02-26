import os
def load(p): return open(p, "r", encoding="utf-8").read()
def setup_batch():
    d = os.path.dirname(os.path.abspath(__file__))
    return {"ref": load(os.path.join(d, "ref.cs")), "compare": load(os.path.join(d, "compare.cs")),
            "batch_name": "02_variable_renaming", "expected_cheating": True, "expected_similarity_range": (70, 95)}
