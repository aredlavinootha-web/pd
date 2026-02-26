using System;

class IsPrime {
    static bool Check(int n) {
        if (n < 2) return false;
        for (int i = 2; i <= (int)Math.Sqrt(n); i++) {
            if (n % i == 0) return false;
        }
        return true;
    }

    static void Main() {
        Console.WriteLine(Check(17));
        Console.WriteLine(Check(20));
    }
}
