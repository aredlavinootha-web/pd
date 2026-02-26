"""
Reference - Original code for Batch 4: Comment Addition
Finds maximum in a list.
"""


def find_max(arr):
    if not arr:
        return None
    max_val = arr[0]
    for x in arr[1:]:
        if x > max_val:
            max_val = x
    return max_val


if __name__ == "__main__":
    data = [3, 7, 2, 9, 1]
    print(find_max(data))
