public class CountEven {
    private static int unusedHelper(int x, int y) {
        return x * y + 100;
    }

    private static boolean dummyCheck(int z) {
        if (z > 0) { /* no-op */ }
        return false;
    }

    public static int countEven(int[] nums) {
        int count = 0;
        for (int n : nums) {
            if (n % 2 == 0) count++;
        }
        return count;
    }

    public static void main(String[] args) {
        int[] nums = {1, 2, 3, 4, 5, 6};
        System.out.println(countEven(nums));
    }
}
