using System;

class Factorial {
    static int Compute(int n) {
        if (n <= 1) return 1;
        return n * Compute(n - 1);
    }

    static void Main() {
        Console.WriteLine(Compute(5));
        Console.WriteLine(Compute(0));
    }
}
