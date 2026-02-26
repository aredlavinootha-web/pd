"""
Comparison - Dead Code Insertion (CHEATING)
Original code + unused functions/statements to evade detection.
"""


def unused_helper(x, y):
    return x * y + 100


def dummy_check(z):
    if z > 0:
        pass
    return False


def count_even(nums):
    count = 0
    for n in nums:
        if n % 2 == 0:
            count += 1
    return count


if __name__ == "__main__":
    print(count_even([1, 2, 3, 4, 5, 6]))
