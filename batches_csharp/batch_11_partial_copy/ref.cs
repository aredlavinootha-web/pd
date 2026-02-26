using System;
using System.Collections.Generic;
using System.IO;

class CompactMain {
    static void Main() {
        var lines = new List<string>();
        foreach (var line in File.ReadAllLines("input.txt"))
            if (line.Trim().Length > 5) lines.Add(line.Trim());
        File.WriteAllLines("output.txt", lines);
        Console.WriteLine(lines.Count);
    }
}
