using System;

// Finds the maximum value in an array
class FindMax {
    // Returns max value
    static int Max(int[] arr) {
        // Edge case check
        if (arr.Length == 0) return int.MinValue;
        // Initialize
        int maxVal = arr[0];
        // Loop
        for (int i = 1; i < arr.Length; i++) {
            // Compare
            if (arr[i] > maxVal) maxVal = arr[i];
        }
        return maxVal;
    }

    // Main entry
    static void Main() {
        int[] data = {3, 7, 2, 9, 1};
        Console.WriteLine(Max(data));
    }
}
