using System;

class BinarySearch {
    static int Search(int[] arr, int target) {
        int lo = 0, hi = arr.Length - 1;
        while (lo <= hi) {
            int mid = (lo + hi) / 2;
            if (arr[mid] == target) return mid;
            if (arr[mid] < target) lo = mid + 1;
            else hi = mid - 1;
        }
        return -1;
    }

    static void Main() {
        int[] a = {1, 3, 5, 7, 9};
        Console.WriteLine(Search(a, 5));
        Console.WriteLine(Search(a, 4));
    }
}
