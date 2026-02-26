using System;

class CountEven {
    static int Count(int[] nums) {
        int count = 0;
        foreach (int n in nums) if (n % 2 == 0) count++;
        return count;
    }

    static void Main() {
        int[] nums = {1, 2, 3, 4, 5, 6};
        Console.WriteLine(Count(nums));
    }
}
