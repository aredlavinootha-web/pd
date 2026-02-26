"""
Reference script - Original code for Batch 2: Variable Renaming
Calculates the sum of squares of numbers in a list.
"""


def sum_of_squares(numbers):
    total = 0
    for num in numbers:
        total += num * num
    return total


def process_list(data):
    return sum_of_squares(data)


if __name__ == "__main__":
    my_list = [1, 2, 3, 4, 5]
    print(process_list(my_list))
