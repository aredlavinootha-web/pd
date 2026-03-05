"""
Measure computation time for plagiarism detection using CopyDetect (same logic as the system).
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
from plagiarism_detect_copydetect import compare_all_pairs_copydetect

NUM_STUDENTS = 100
TOP_N = 10


def main():
    print("Generating 100 Python student submissions...")
    students = generate_student_submissions(n=NUM_STUDENTS)
    print(f"Generated {len(students)} submissions.\n")

    print("Running CopyDetect all-pairs comparison (100 students)...")
    start = time.perf_counter()
    result = compare_all_pairs_copydetect(
        students,
        language="python",
        top_n=TOP_N,
    )
    elapsed = time.perf_counter() - start

    if not result.get("available"):
        print("Error:", result.get("error", "CopyDetect unavailable"))
        return

    top_matches = result.get("top_matches_per_student", {})
    print(f"\nComparisons: {result.get('comparisons_count')}, Students: {result.get('students_count')}\n")

    print("=" * 70)
    print("TOP 10 MATCHES PER STUDENT (CopyDetect)")
    print("=" * 70)
    for sid in sorted(top_matches.keys(), key=lambda x: int(x.split("_")[1])):
        matches = top_matches[sid]
        print(f"\n{sid}:")
        for rank, m in enumerate(matches, 1):
            other_id = m["other_student_id"]
            sim = m["similarity"]
            pct = sim * 100
            print(f"  {rank:2}. {other_id}  {pct:6.2f}%")

    print("\n" + "=" * 70)
    print(f"TOTAL COMPUTATION TIME (CopyDetect, 100 students): {elapsed:.3f} seconds")
    print("=" * 70)


if __name__ == "__main__":
    main()
