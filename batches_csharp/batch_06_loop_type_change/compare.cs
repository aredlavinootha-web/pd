using System;

class SumList {
    static int Sum(int[] nums) {
        int total = 0, i = 0;
        while (i < nums.Length) { total += nums[i]; i++; }
        return total;
    }

    static void Main() {
        int[] nums = {1, 2, 3, 4, 5};
        Console.WriteLine(Sum(nums));
    }
}
