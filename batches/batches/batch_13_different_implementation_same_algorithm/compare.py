"""
Comparison - Different Implementation Same Algorithm (NOT cheating)
Same binary search, different variable names and structure.
"""


def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        center = left + (right - left) // 2
        val = arr[center]
        if val == target:
            return center
        if val < target:
            left = center + 1
        else:
            right = center - 1
    return -1


if __name__ == "__main__":
    a = [1, 3, 5, 7, 9]
    print(binary_search(a, 5))
    print(binary_search(a, 4))
