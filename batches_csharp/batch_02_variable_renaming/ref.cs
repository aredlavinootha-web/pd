using System;

class SumOfSquares {
    static int SumSquares(int[] numbers) {
        int total = 0;
        foreach (int num in numbers) total += num * num;
        return total;
    }

    static int ProcessList(int[] data) => SumSquares(data);

    static void Main() {
        int[] myList = {1, 2, 3, 4, 5};
        Console.WriteLine(ProcessList(myList));
    }
}
