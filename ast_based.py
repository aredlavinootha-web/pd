"""
Measure computation time for plagiarism detection using AST comparison (tree-sitter Python).
100 student submissions, pairwise comparison, top 10 matches per student.

Optional: set memory limit (e.g. 2 GB) with env var MAX_MEMORY_MB=2048 (Linux/Unix only).
"""

import os
import sys
import time

# Ensure project root is on path
sys.path.insert(0, ".")

# Optional memory limit (must be set before heavy imports). Linux/Unix only.
_max_mb = os.environ.get("MAX_MEMORY_MB")
if _max_mb:
    try:
        import resource
        _limit_bytes = int(_max_mb) * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (_limit_bytes, _limit_bytes))
        print(f"[Memory limit: {_max_mb} MB]\n")
    except (ValueError, OSError, ImportError) as e:
        print(f"Warning: could not set memory limit ({_max_mb} MB): {e}\n")

from generate_student_codes import generate_student_submissions
from plagiarism_detect_treesitter_python import compare_code_treesitter_python

NUM_STUDENTS = 100
TOP_N = 10


def main():
    print("Generating 100 Python student submissions...")
    students = generate_student_submissions(n=NUM_STUDENTS)
    print(f"Generated {len(students)} submissions.\n")

    print("Running AST (tree-sitter) pairwise comparison (100 students)...")
    start = time.perf_counter()

    top_matches_per_student = {}
    for i, student in enumerate(students):
        main_id = student["id"]
        main_code = student["code"]
        other_students = [{"id": s["id"], "code": s["code"]} for j, s in enumerate(students) if j != i]
        result = compare_code_treesitter_python(main_id, main_code, other_students)
        if not result.get("available") or not result.get("results"):
            top_matches_per_student[main_id] = []
            continue
        results = result["results"]
        results.sort(key=lambda r: r.get("similarity", 0.0), reverse=True)
        top_matches_per_student[main_id] = [
            {"other_student_id": r["other_student_id"], "similarity": r["similarity"]}
            for r in results[:TOP_N]
        ]

    elapsed = time.perf_counter() - start

    total_pairs = NUM_STUDENTS * (NUM_STUDENTS - 1) // 2
    print(f"\nComparisons: {total_pairs}, Students: {NUM_STUDENTS}\n")

    print("=" * 70)
    print("TOP 10 MATCHES PER STUDENT (AST / tree-sitter)")
    print("=" * 70)
    for sid in sorted(top_matches_per_student.keys(), key=lambda x: int(x.split("_")[1])):
        matches = top_matches_per_student[sid]
        print(f"\n{sid}:")
        for rank, m in enumerate(matches, 1):
            other_id = m["other_student_id"]
            sim = m["similarity"]
            pct = sim * 100
            print(f"  {rank:2}. {other_id}  {pct:6.2f}%")

    print("\n" + "=" * 70)
    print(f"TOTAL COMPUTATION TIME (AST, 100 students): {elapsed:.3f} seconds")
    print("=" * 70)


if __name__ == "__main__":
    main()
