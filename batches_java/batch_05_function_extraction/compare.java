public class Palindrome {
    public static boolean isPalindrome(String s) {
        s = s.toLowerCase().replace(" ", "");
        int left = 0, right = s.length() - 1;
        while (left < right) {
            if (s.charAt(left) != s.charAt(right)) return false;
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
