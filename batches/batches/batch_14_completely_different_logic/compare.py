"""
Comparison - Completely Different Logic (Control, NOT cheating)
Same task (sorting), entirely different algorithm: quicksort.
"""


def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)


if __name__ == "__main__":
    data = [64, 34, 25, 12, 22, 11, 90]
    print(quicksort(data.copy()))
