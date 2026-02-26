"""
Reference script - Original code for Batch 1: Exact Copy
Computes factorial of a number using iterative approach.
"""


def factorial(n):
    if n < 0:
        return None
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


if __name__ == "__main__":
    print(factorial(5))
    print(factorial(0))
