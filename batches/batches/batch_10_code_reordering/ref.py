"""
Reference - Original code for Batch 10: Code Reordering
Computes stats for a list.
"""


def compute_stats(data):
    total = sum(data)
    n = len(data)
    avg = total / n if n else 0
    mx = max(data)
    mn = min(data)
    return avg, mx, mn


if __name__ == "__main__":
    d = [10, 20, 30, 40, 50]
    print(compute_stats(d))
