using System;

class BinarySearch {
    static int Search(int[] arr, int target) {
        int left = 0, right = arr.Length - 1;
        while (left <= right) {
            int center = left + (right - left) / 2;
            if (arr[center] == target) return center;
            if (arr[center] < target) left = center + 1;
            else right = center - 1;
        }
        return -1;
    }

    static void Main() {
        int[] a = {1, 3, 5, 7, 9};
        Console.WriteLine(Search(a, 5));
        Console.WriteLine(Search(a, 4));
    }
}
