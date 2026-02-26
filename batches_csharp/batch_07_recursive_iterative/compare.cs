using System;

class Factorial {
    static int Compute(int n) {
        int result = 1;
        for (int i = 2; i <= n; i++) result *= i;
        return result;
    }

    static void Main() {
        Console.WriteLine(Compute(5));
        Console.WriteLine(Compute(0));
    }
}
