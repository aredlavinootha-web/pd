"""
Comparison - Code Reordering (CHEATING)
Same logic, independent statements reordered.
"""


def compute_stats(data):
    n = len(data)
    mx = max(data)
    mn = min(data)
    total = sum(data)
    avg = total / n if n else 0
    return avg, mx, mn


if __name__ == "__main__":
    d = [10, 20, 30, 40, 50]
    print(compute_stats(d))
