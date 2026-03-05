"""
Load 100 medium-sized real-world Python submissions from sample_data for benchmarking.
Creates sample_data/ with student_001.py ... student_100.py if missing.
"""

import os
import re
import random

# Default directory for sample student code (medium-sized, real-world style)
SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
NUM_STUDENTS = 100


def _templates() -> list[str]:
    """Medium-sized real-world code snippets (~25-50 lines each)."""
    return [
        '''"""
Computes factorial of a number using iterative approach.
"""


def factorial(n):
    if n < 0:
        return None
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


if __name__ == "__main__":
    print(factorial(5))
    print(factorial(0))
''',
        '''"""
Reference - Calculates the sum of squares of numbers in a list.
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
''',
        '''"""
Factorial using recursive approach.
"""


def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)


if __name__ == "__main__":
    print(factorial(5))
    print(factorial(0))
''',
        '''"""
Binary search - iterative implementation.
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
''',
        '''"""
Checks if string is palindrome.
"""


def is_palindrome(s):
    s = s.lower().replace(" ", "")
    left, right = 0, len(s) - 1
    while left < right:
        if s[left] != s[right]:
            return False
        left += 1
        right -= 1
    return True


if __name__ == "__main__":
    print(is_palindrome("A man a plan a canal Panama"))
    print(is_palindrome("hello"))
''',
        '''"""
Sum numbers in a list using for-loop.
"""


def sum_list(nums):
    total = 0
    for n in nums:
        total += n
    return total


if __name__ == "__main__":
    print(sum_list([1, 2, 3, 4, 5]))
''',
        '''"""
Finds maximum value in a list.
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
''',
        '''"""
Reads file, filters lines by length, writes output.
"""


def main():
    with open("input.txt", "r") as f:
        lines = f.readlines()
    filtered = [line.strip() for line in lines if len(line.strip()) > 5]
    with open("output.txt", "w") as f:
        f.write("\\n".join(filtered))
    return len(filtered)


if __name__ == "__main__":
    main()
''',
        '''"""
Greatest common divisor using Euclidean algorithm.
"""


def gcd(a, b):
    while b:
        a, b = b, a % b
    return a


if __name__ == "__main__":
    print(gcd(48, 18))
    print(gcd(100, 35))
''',
        '''"""
Check if a number is prime.
"""


def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True


if __name__ == "__main__":
    print(is_prime(17))
    print(is_prime(20))
''',
        '''"""
Reverse a list and return new list.
"""


def reverse_list(lst):
    result = []
    for i in range(len(lst) - 1, -1, -1):
        result.append(lst[i])
    return result


if __name__ == "__main__":
    print(reverse_list([1, 2, 3, 4, 5]))
''',
        '''"""
Count vowels in a string.
"""


def count_vowels(s):
    vowels = "aeiouAEIOU"
    count = 0
    for c in s:
        if c in vowels:
            count += 1
    return count


if __name__ == "__main__":
    print(count_vowels("Hello World"))
''',
        '''"""
Sum each row of a 2D list (matrix).
"""


def row_sums(matrix):
    sums = []
    for row in matrix:
        row_total = 0
        for val in row:
            row_total += val
        sums.append(row_total)
    return sums


if __name__ == "__main__":
    m = [[1, 2], [3, 4], [5, 6]]
    print(row_sums(m))
''',
        '''"""
Linear search for target in list.
"""


def linear_search(arr, target):
    for i in range(len(arr)):
        if arr[i] == target:
            return i
    return -1


if __name__ == "__main__":
    data = [10, 20, 30, 40, 50]
    print(linear_search(data, 30))
    print(linear_search(data, 99))
''',
        '''"""
Fibonacci sequence - iterative version.
"""


def fibonacci(n):
    if n <= 0:
        return 0
    if n == 1:
        return 1
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


if __name__ == "__main__":
    for i in range(10):
        print(fibonacci(i), end=" ")
''',
        '''"""
Bubble sort - sorts list in place.
"""


def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr


if __name__ == "__main__":
    a = [64, 34, 25, 12, 22]
    print(bubble_sort(a))
''',
        '''"""
Find minimum value in a list.
"""


def find_min(arr):
    if not arr:
        return None
    min_val = arr[0]
    for x in arr[1:]:
        if x < min_val:
            min_val = x
    return min_val


if __name__ == "__main__":
    data = [3, 7, 2, 9, 1]
    print(find_min(data))
''',
        '''"""
Count occurrences of key in list.
"""


def count_occurrences(lst, key):
    count = 0
    for item in lst:
        if item == key:
            count += 1
    return count


if __name__ == "__main__":
    data = [1, 2, 2, 3, 2, 4]
    print(count_occurrences(data, 2))
''',
        '''"""
Compute average of numbers in list.
"""


def average(nums):
    if not nums:
        return 0
    total = sum_list(nums)
    return total / len(nums)


def sum_list(nums):
    s = 0
    for n in nums:
        s += n
    return s


if __name__ == "__main__":
    print(average([10, 20, 30, 40, 50]))
''',
        '''"""
Remove duplicates from list preserving order.
"""


def unique_list(lst):
    seen = []
    for x in lst:
        if x not in seen:
            seen.append(x)
    return seen


if __name__ == "__main__":
    print(unique_list([1, 2, 2, 3, 1, 4, 3]))
''',
    ]


def _variation(code: str, seed: int) -> str:
    """Apply light variation (variable renames, extra newline) for diversity."""
    rng = random.Random(seed)
    # Optional extra newline after first docstring
    if rng.random() < 0.3:
        code = code.replace('"""\n\n', '"""\n\n\n', 1)
    return code


def ensure_sample_data(dir_path: str | None = None, n: int = NUM_STUDENTS) -> str:
    """Create sample_data with n medium-sized Python files. Returns directory path."""
    base = dir_path or SAMPLE_DATA_DIR
    os.makedirs(base, exist_ok=True)
    templates = _templates()
    for i in range(n):
        sid = f"student_{i + 1:03d}"
        code = templates[i % len(templates)]
        code = _variation(code, seed=i)
        path = os.path.join(base, f"{sid}.py")
        with open(path, "w", encoding="utf-8") as f:
            f.write(code)
    return base


def load_student_submissions(sample_dir: str | None = None, n: int = NUM_STUDENTS) -> list[dict]:
    """
    Load student submissions from sample_data (student_001.py ... student_NNN.py).
    If sample_data has fewer than n files, ensure_sample_data is called first.
    """
    base = sample_dir or SAMPLE_DATA_DIR
    if not os.path.isdir(base):
        ensure_sample_data(base, n)
    students = []
    for i in range(1, n + 1):
        sid = f"student_{i:03d}"
        path = os.path.join(base, f"{sid}.py")
        if not os.path.isfile(path):
            ensure_sample_data(base, n)
            break
    # Reload after possibly creating
    for i in range(1, n + 1):
        sid = f"student_{i:03d}"
        path = os.path.join(base, f"{sid}.py")
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                code = f.read()
            students.append({"id": sid, "code": code})
    if len(students) < n:
        ensure_sample_data(base, n)
        return load_student_submissions(base, n)
    return students


def generate_student_submissions(n: int = NUM_STUDENTS, seed: int = 42) -> list[dict]:
    """
    Return n student submissions with id and code (medium-sized real-world style).
    Uses sample_data/; creates it if missing.
    """
    ensure_sample_data(SAMPLE_DATA_DIR, n)
    return load_student_submissions(SAMPLE_DATA_DIR, n)
