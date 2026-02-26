using System;

class CountEven {
    static int UnusedHelper(int x, int y) => x * y + 100;
    static bool DummyCheck(int z) { if (z > 0) { } return false; }

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
