public class Palindrome {
    private static String normalize(String s) {
        return s.toLowerCase().replace(" ", "");
    }

    private static boolean charsMatch(String s, int left, int right) {
        return s.charAt(left) == s.charAt(right);
    }

    public static boolean isPalindrome(String s) {
        s = normalize(s);
        int left = 0, right = s.length() - 1;
        while (left < right) {
            if (!charsMatch(s, left, right)) return false;
            left++;
            right--;
        }
        return true;
    }

    public static void main(String[] args) {
        System.out.println(isPalindrome("A man a plan a canal Panama"));
        System.out.println(isPalindrome("hello"));
    }
}
