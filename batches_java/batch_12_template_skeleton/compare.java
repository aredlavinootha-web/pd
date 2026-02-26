import java.io.*;

public class TextTransform {
    public static String transform(String input) {
        return input.toUpperCase();
    }

    public static void main(String[] args) throws IOException {
        if (args.length < 2) { System.err.println("Usage: input output"); return; }
        BufferedReader br = new BufferedReader(new FileReader(args[0]));
        StringBuilder sb = new StringBuilder();
        String line;
        while ((line = br.readLine()) != null) sb.append(line).append("\n");
        br.close();
        String result = transform(sb.toString());
        PrintWriter pw = new PrintWriter(new FileWriter(args[1]));
        pw.print(result);
        pw.close();
    }
}
