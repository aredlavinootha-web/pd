"""
Reference - Original code for Batch 7: Recursive↔Iterative (NOT cheating)
Factorial using recursive approach.
"""


def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)


if __name__ == "__main__":
    print(factorial(5))
    print(factorial(0))
