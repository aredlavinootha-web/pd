"""
Comparison - Comment Addition (CHEATING)
Original code with extra comments added to evade detection.
"""


# Function to find maximum value
def find_max(arr):
    # Check if list is empty
    if not arr:
        return None
    # Initialize with first element
    max_val = arr[0]
    # Loop through remaining elements
    for x in arr[1:]:
        # Update if larger found
        if x > max_val:
            max_val = x
    return max_val


# Main execution block
if __name__ == "__main__":
    data = [3, 7, 2, 9, 1]
    print(find_max(data))
