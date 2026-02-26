using System;

class MaxOfTwo {
    static int Max(int a, int b) {
        if (a > b) return a;
        return b;
    }

    static void Main() {
        Console.WriteLine(Max(3, 7));
        Console.WriteLine(Max(10, 5));
    }
}
