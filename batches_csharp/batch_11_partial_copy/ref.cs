using System;
using System.Collections.Generic;
using System.IO;

class ProcessData {
    static List<string> FetchLines(string path) => new List<string>(File.ReadAllLines(path));

    static void SaveResults(List<string> items, string path) => File.WriteAllLines(path, items);

    static int Process() {
        var data = FetchLines("input.txt");
        var filtered = new List<string>();
        foreach (var x in data) if (x.Trim().Length > 5) filtered.Add(x.Trim());
        SaveResults(filtered, "output.txt");
        return filtered.Count;
    }

    static void Main() => Console.WriteLine(Process());
}
