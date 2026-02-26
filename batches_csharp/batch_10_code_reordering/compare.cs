using System;

class Stats {
    static (double avg, int max, int min) Compute(int[] data) {
        int total = 0;
        foreach (int v in data) total += v;
        double avg = data.Length > 0 ? (double)total / data.Length : 0;
        int mx = data[0], mn = data[0];
        foreach (int v in data) {
            if (v > mx) mx = v;
            if (v < mn) mn = v;
        }
        return (avg, mx, mn);
    }

    static void Main() {
        int[] d = {10, 20, 30, 40, 50};
        var r = Compute(d);
        Console.WriteLine($"avg={r.avg:F1} max={r.max} min={r.min}");
    }
}
