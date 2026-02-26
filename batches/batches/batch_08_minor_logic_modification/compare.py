"""
Comparison - Minor Logic Modification (CHEATING)
Equivalent condition changes: a>b → b<=a, etc.
"""


def max_of_two(a, b):
    if b <= a:
        return a
    return b


if __name__ == "__main__":
    print(max_of_two(3, 7))
    print(max_of_two(10, 5))
