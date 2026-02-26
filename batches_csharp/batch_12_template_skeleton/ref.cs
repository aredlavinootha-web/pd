using System;
using System.IO;

class TextTransform {
    static string Transform(string s) => s.ToLower();

    static void Main(string[] args) {
        if (args.Length < 2) { Console.Error.WriteLine("Usage: input output"); return; }
        string data = File.ReadAllText(args[0]);
        File.WriteAllText(args[1], Transform(data));
    }
}
