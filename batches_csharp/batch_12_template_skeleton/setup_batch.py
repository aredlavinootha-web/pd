import os
def load(p): return open(p, "r", encoding="utf-8").read()
def setup_batch():
    d = os.path.dirname(os.path.abspath(__file__))
    return {"ref": load(os.path.join(d, "ref.cs")), "compare": load(os.path.join(d, "compare.cs")),
            "batch_name": "12_template_skeleton", "expected_cheating": False, "expected_similarity_range": (20, 45)}
