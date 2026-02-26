using System;

class SelectionSort {
    static void Sort(int[] arr) {
        for (int i = 0; i < arr.Length; i++) {
            int minIdx = i;
            for (int j = i + 1; j < arr.Length; j++)
                if (arr[j] < arr[minIdx]) minIdx = j;
            int tmp = arr[i]; arr[i] = arr[minIdx]; arr[minIdx] = tmp;
        }
    }

    static void Main() {
        int[] data = {64, 34, 25, 12, 22, 11, 90};
        Sort(data);
        Console.WriteLine(string.Join(", ", data));
    }
}
