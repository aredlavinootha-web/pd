"""
Reference - Original code for Batch 5: Function Extraction
Checks if string is palindrome (inline logic).
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
