"""
Comparison - Recursive↔Iterative (NOT cheating)
Same logic, iterative instead of recursive.
"""


def factorial(n):
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


if __name__ == "__main__":
    print(factorial(5))
    print(factorial(0))
