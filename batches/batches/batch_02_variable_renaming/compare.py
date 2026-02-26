"""
Comparison script - Variable Renaming (CHEATING)
Same logic as ref, only variable and function names changed.
"""


def compute_quadratic_sum(elements):
    accumulator = 0
    for value in elements:
        accumulator += value * value
    return accumulator


def handle_input(collection):
    return compute_quadratic_sum(collection)


if __name__ == "__main__":
    input_data = [1, 2, 3, 4, 5]
    print(handle_input(input_data))
