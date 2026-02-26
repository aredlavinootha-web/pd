using System;

class BinarySearch {
    static int SearchRec(int[] arr, int lo, int hi, int target) {
        if (lo > hi) return -1;
        int mid = lo + (hi - lo) / 2;
        if (arr[mid] == target) return mid;
        if (arr[mid] < target) return SearchRec(arr, mid + 1, hi, target);
        return SearchRec(arr, lo, mid - 1, target);
    }

    static int Search(int[] arr, int target) {
        return SearchRec(arr, 0, arr.Length - 1, target);
    }

    static void Main() {
        int[] a = {1, 3, 5, 7, 9};
        Console.WriteLine(Search(a, 5));
        Console.WriteLine(Search(a, 4));
    }
}
