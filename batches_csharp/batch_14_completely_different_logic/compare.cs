using System;
using System.Collections.Generic;

class QuickSort {
    static List<int> Sort(List<int> arr) {
        if (arr.Count <= 1) return arr;
        int pivot = arr[arr.Count / 2];
        var left = new List<int>(); var mid = new List<int>(); var right = new List<int>();
        foreach (int x in arr) {
            if (x < pivot) left.Add(x);
            else if (x == pivot) mid.Add(x);
            else right.Add(x);
        }
        var result = Sort(left); result.AddRange(mid); result.AddRange(Sort(right));
        return result;
    }

    static void Main() {
        var data = new List<int> {64, 34, 25, 12, 22, 11, 90};
        Console.WriteLine(string.Join(", ", Sort(data)));
    }
}
