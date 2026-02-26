"""
Reference - Original code for Batch 13: Different Implementation Same Algorithm (NOT cheating)
Binary search - verbose style.
"""


def binary_search(arr, target):
    lo = 0
    hi = len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


if __name__ == "__main__":
    a = [1, 3, 5, 7, 9]
    print(binary_search(a, 5))
    print(binary_search(a, 4))
