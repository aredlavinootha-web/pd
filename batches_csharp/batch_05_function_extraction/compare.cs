using System;

class Palindrome {
    static string Normalize(string s) => s.ToLower().Replace(" ", "");
    static bool CharsMatch(string s, int l, int r) => s[l] == s[r];

    static bool IsPalindrome(string s) {
        s = Normalize(s);
        int left = 0, right = s.Length - 1;
        while (left < right) {
            if (!CharsMatch(s, left, right)) return false;
            left++; right--;
        }
        return true;
    }

    static void Main() {
        Console.WriteLine(IsPalindrome("A man a plan a canal Panama"));
        Console.WriteLine(IsPalindrome("hello"));
    }
}
