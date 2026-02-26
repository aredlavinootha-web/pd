"""
Reference - Original code for Batch 6: Loop Type Change (NOT cheating)
Sum numbers using for-loop.
"""


def sum_list(nums):
    total = 0
    for n in nums:
        total += n
    return total


if __name__ == "__main__":
    print(sum_list([1, 2, 3, 4, 5]))
