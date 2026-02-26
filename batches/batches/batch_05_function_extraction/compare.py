"""
Comparison - Function Extraction (CHEATING)
Same logic split into helper functions to evade detection.
"""


def normalize(s):
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
    print(is_palindrome("hello"))
