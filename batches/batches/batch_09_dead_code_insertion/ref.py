"""
Reference - Original code for Batch 9: Dead Code Insertion
Counts even numbers in list.
"""


def count_even(nums):
    count = 0
    for n in nums:
        if n % 2 == 0:
            count += 1
    return count


if __name__ == "__main__":
    print(count_even([1, 2, 3, 4, 5, 6]))
