using System;

class Palindrome {
    static bool IsPalindrome(string s) {
        s = s.ToLower().Replace(" ", "");
        int left = 0, right = s.Length - 1;
        while (left < right) {
            if (s[left] != s[right]) return false;
            left++; right--;
        }
        return true;
    }

    static void Main() {
        Console.WriteLine(IsPalindrome("A man a plan a canal Panama"));
        Console.WriteLine(IsPalindrome("hello"));
    }
}
