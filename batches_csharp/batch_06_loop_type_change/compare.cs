using System;

class SumList {
    static int Sum(int[] nums) {
        int total = 0;
        foreach (int n in nums) total += n;
        return total;
    }

    static void Main() {
        int[] nums = {1, 2, 3, 4, 5};
        Console.WriteLine(Sum(nums));
    }
}
