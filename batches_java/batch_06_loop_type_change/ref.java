public class SumList {
    public static int sumList(int[] nums) {
        int total = 0;
        int i = 0;
        while (i < nums.length) {
            total += nums[i];
            i++;
        }
        return total;
    }

    public static void main(String[] args) {
        int[] nums = {1, 2, 3, 4, 5};
        System.out.println(sumList(nums));
    }
}
