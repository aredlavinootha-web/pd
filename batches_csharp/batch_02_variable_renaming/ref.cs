using System;

class SumOfSquares {
    static int ComputeQuadraticSum(int[] elements) {
        int accumulator = 0;
        foreach (int value in elements) accumulator += value * value;
        return accumulator;
    }

    static int HandleInput(int[] collection) => ComputeQuadraticSum(collection);

    static void Main() {
        int[] inputData = {1, 2, 3, 4, 5};
        Console.WriteLine(HandleInput(inputData));
    }
}
