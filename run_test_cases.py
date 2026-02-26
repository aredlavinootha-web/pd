"""
Run all 14 test cases through the 4 tree-sitter tools + difflib + copydetect
and print a comparison report.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from plagiarism_detect_copydetect import compare_code_copydetect
from plagiarism_detect_difflib import compare_code_difflib
from plagiarism_detect_treesitter_python import compare_code_treesitter_python
from plagiarism_detect_treesitter_cpp import compare_code_treesitter_cpp
from plagiarism_detect_treesitter_java import compare_code_treesitter_java
from plagiarism_detect_treesitter_c import compare_code_treesitter_c
from plagiarism_detect_treesitter_csharp import compare_code_treesitter_csharp
from plagiarism_detect_treesitter_javascript import compare_code_treesitter_javascript

# ---------------------------------------------------------------------------
# Test cases: (label, code_a, code_b, expected_range, cheating)
# ---------------------------------------------------------------------------
CASES = [
    (
        "Exact Copy",
        """def factorial(n):
    if n < 0:
        return None
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

if __name__ == "__main__":
    print(factorial(5))
    print(factorial(0))""",
        """def factorial(n):
    if n < 0:
        return None
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

if __name__ == "__main__":
    print(factorial(5))
    print(factorial(0))""",
        "95-100", "yes",
    ),
    (
        "Variable Renaming",
        """def compute_quadratic_sum(elements):
    accumulator = 0
    for value in elements:
        accumulator += value * value
    return accumulator

def handle_input(collection):
    return compute_quadratic_sum(collection)

if __name__ == "__main__":
    input_data = [1, 2, 3, 4, 5]
    print(handle_input(input_data))""",
        """def sum_of_squares(numbers):
    total = 0
    for num in numbers:
        total += num * num
    return total

def process_list(data):
    return sum_of_squares(data)

if __name__ == "__main__":
    my_list = [1, 2, 3, 4, 5]
    print(process_list(my_list))""",
        "70-95", "yes",
    ),
    (
        "Whitespace / Formatting",
        """def is_prime(n):
    if n<2:
        return False
    for i in range(2,int(n**0.5)+1):
        if n%i==0:
            return False
    return True

if __name__=="__main__":
    print(is_prime(17)); print(is_prime(20))""",
        """def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

if __name__ == "__main__":
    print(is_prime(17))
    print(is_prime(20))""",
        "90-100", "yes",
    ),
    (
        "Comment Add / Remove",
        """# Function to find maximum value
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
    print(find_max(data))""",
        """def find_max(arr):
    if not arr:
        return None
    max_val = arr[0]
    for x in arr[1:]:
        if x > max_val:
            max_val = x
    return max_val

if __name__ == "__main__":
    data = [3, 7, 2, 9, 1]
    print(find_max(data))""",
        "85-100", "yes",
    ),
    (
        "Function Extraction / Inlining",
        """def normalize(s):
    return s.lower().replace(" ", "")

def compare_chars(s, left, right):
    return s[left] != s[right]

def is_palindrome(s):
    s = normalize(s)
    left, right = 0, len(s) - 1
    while left < right:
        if compare_chars(s, left, right):
            return False
        left += 1
        right -= 1
    return True

if __name__ == "__main__":
    print(is_palindrome("A man a plan a canal Panama"))
    print(is_palindrome("hello"))""",
        """def is_palindrome(s):
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
    print(is_palindrome("hello"))""",
        "55-85", "yes",
    ),
    (
        "Loop Type (for ↔ while)",
        """def sum_list(nums):
    total = 0
    i = 0
    while i < len(nums):
        total += nums[i]
        i += 1
    return total

if __name__ == "__main__":
    print(sum_list([1, 2, 3, 4, 5]))""",
        """def sum_list(nums):
    total = 0
    for n in nums:
        total += n
    return total

if __name__ == "__main__":
    print(sum_list([1, 2, 3, 4, 5]))""",
        "45-65", "no",
    ),
    (
        "Recursive ↔ Iterative",
        """def factorial(n):
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

if __name__ == "__main__":
    print(factorial(5))
    print(factorial(0))""",
        """def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

if __name__ == "__main__":
    print(factorial(5))
    print(factorial(0))""",
        "25-50", "no",
    ),
    (
        "Minor Logic Modification",
        """def max_of_two(a, b):
    if b <= a:
        return a
    return b

if __name__ == "__main__":
    print(max_of_two(3, 7))
    print(max_of_two(10, 5))""",
        """def max_of_two(a, b):
    if a > b:
        return a
    return b

if __name__ == "__main__":
    print(max_of_two(3, 7))
    print(max_of_two(10, 5))""",
        "75-95", "yes",
    ),
    (
        "Dead Code Insertion",
        """def unused_helper(x, y):
    return x * y + 100

def dummy_check(z):
    if z > 0:
        pass
    return False

def count_even(nums):
    count = 0
    for n in nums:
        if n % 2 == 0:
            count += 1
    return count

if __name__ == "__main__":
    print(count_even([1, 2, 3, 4, 5, 6]))""",
        """def count_even(nums):
    count = 0
    for n in nums:
        if n % 2 == 0:
            count += 1
    return count

if __name__ == "__main__":
    print(count_even([1, 2, 3, 4, 5, 6]))""",
        "60-85", "yes",
    ),
    (
        "Code Reordering",
        """def compute_stats(data):
    n = len(data)
    mx = max(data)
    mn = min(data)
    total = sum(data)
    avg = total / n if n else 0
    return avg, mx, mn

if __name__ == "__main__":
    d = [10, 20, 30, 40, 50]
    print(compute_stats(d))""",
        """def compute_stats(data):
    total = sum(data)
    n = len(data)
    avg = total / n if n else 0
    mx = max(data)
    mn = min(data)
    return avg, mx, mn

if __name__ == "__main__":
    d = [10, 20, 30, 40, 50]
    print(compute_stats(d))""",
        "70-90", "yes",
    ),
    (
        "Partial Copy / Restructure",
        """def process_data():
    data = fetch_from_db()
    filtered = [x for x in data if len(str(x).strip()) > 5]
    save_results(filtered)
    return len(filtered)

def fetch_from_db():
    with open("input.txt", "r") as f:
        return f.readlines()

def save_results(items):
    with open("output.txt", "w") as f:
        f.write("\\n".join(str(i).strip() for i in items))

if __name__ == "__main__":
    process_data()""",
        """def main():
    with open("input.txt", "r") as f:
        lines = f.readlines()
    filtered = [line.strip() for line in lines if len(line.strip()) > 5]
    with open("output.txt", "w") as f:
        f.write("\\n".join(filtered))
    return len(filtered)

if __name__ == "__main__":
    main()""",
        "40-70", "yes",
    ),
    (
        "Template / Skeleton (Boilerplate)",
        """import sys
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Process data")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", default="out.txt")
    return parser.parse_args()

def main():
    args = parse_args()
    with open(args.input) as f:
        data = f.read()
    result = data.lower()
    with open(args.output, "w") as f:
        f.write(result)

if __name__ == "__main__":
    main()""",
        """import sys
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Process data")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", default="out.txt")
    return parser.parse_args()

def main():
    args = parse_args()
    with open(args.input) as f:
        data = f.read()
    result = data.upper()
    with open(args.output, "w") as f:
        f.write(result)

if __name__ == "__main__":
    main()""",
        "20-45 (core logic)", "no",
    ),
    (
        "Different Implementation, Same Algorithm",
        """def binary_search(arr, target):
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
    print(binary_search(a, 4))""",
        """def binary_search(arr, target):
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
    print(binary_search(a, 4))""",
        "45-75", "no",
    ),
    (
        "Completely Different Logic",
        """def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)

if __name__ == "__main__":
    data = [64, 34, 25, 12, 22, 11, 90]
    print(quicksort(data.copy()))""",
        """def selection_sort(arr):
    for i in range(len(arr)):
        min_idx = i
        for j in range(i + 1, len(arr)):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr

if __name__ == "__main__":
    data = [64, 34, 25, 12, 22, 11, 90]
    print(selection_sort(data.copy()))""",
        "10-35", "no",
    ),
]

TOOLS = [
    ("treesitter_python", lambda a, b: compare_code_treesitter_python("main", a, [{"id": "other", "code": b}])),
    ("treesitter_cpp",    lambda a, b: compare_code_treesitter_cpp("main", a, [{"id": "other", "code": b}])),
    ("treesitter_java",   lambda a, b: compare_code_treesitter_java("main", a, [{"id": "other", "code": b}])),
    ("treesitter_c",      lambda a, b: compare_code_treesitter_c("main", a, [{"id": "other", "code": b}])),
    ("treesitter_csharp", lambda a, b: compare_code_treesitter_csharp("main", a, [{"id": "other", "code": b}])),
    ("treesitter_js",     lambda a, b: compare_code_treesitter_javascript("main", a, [{"id": "other", "code": b}])),
]


def get_similarity(result: dict) -> str:
    if not result.get("available"):
        return "N/A"
    results = result.get("results", [])
    if not results:
        return "N/A"
    sim = results[0].get("similarity")
    if sim is None:
        return "N/A"
    return f"{sim * 100:.1f}%"


def run():
    col_w = 22
    tool_names = [t[0] for t in TOOLS]

    # Header
    header_case = "Case".ljust(38)
    header_cheat = "Cheat".ljust(6)
    header_exp = "Expected".ljust(22)
    header_tools = "  ".join(t.ljust(col_w) for t in tool_names)
    sep = "-" * (38 + 6 + 22 + len(tool_names) * (col_w + 2))

    print()
    print("=" * len(sep))
    print("PLAGIARISM DETECTOR — TEST CASE REPORT")
    print("=" * len(sep))
    print()
    print(f"{header_case}{header_cheat}{header_exp}{header_tools}")
    print(sep)

    for label, code_a, code_b, expected, cheating in CASES:
        scores = []
        for tool_name, tool_fn in TOOLS:
            try:
                result = tool_fn(code_a, code_b)
                score = get_similarity(result)
            except Exception as e:
                score = f"ERR"
            scores.append(score.ljust(col_w))

        row_case = label[:37].ljust(38)
        row_cheat = cheating.ljust(6)
        row_exp = expected.ljust(22)
        row_scores = "  ".join(scores)
        print(f"{row_case}{row_cheat}{row_exp}{row_scores}")

    print(sep)
    print()
    print("Tools note:")
    print("  treesitter_cpp / java / js parse Python code with wrong grammars — scores are structural noise.")
    print("  treesitter_python gives semantically meaningful AST similarity for Python code.")
    print()


if __name__ == "__main__":
    run()
