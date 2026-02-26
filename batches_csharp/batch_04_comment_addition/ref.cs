using System;

class FindMax {
    static int Max(int[] arr) {
        if (arr.Length == 0) return int.MinValue;
        int maxVal = arr[0];
        for (int i = 1; i < arr.Length; i++) {
            if (arr[i] > maxVal) maxVal = arr[i];
        }
        return maxVal;
    }

    static void Main() {
        int[] data = {3, 7, 2, 9, 1};
        Console.WriteLine(Max(data));
    }
}
