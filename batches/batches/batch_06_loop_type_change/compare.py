"""
Comparison - Loop Type Change for↔while (NOT cheating)
Same logic, for-loop rewritten as while-loop.
"""


def sum_list(nums):
    total = 0
    i = 0
    while i < len(nums):
        total += nums[i]
        i += 1
    return total


if __name__ == "__main__":
    print(sum_list([1, 2, 3, 4, 5]))
