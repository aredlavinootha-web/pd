import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        List<String> lines = new ArrayList<>();
        try (BufferedReader br = new BufferedReader(new FileReader("input.txt"))) {
            String line;
            while ((line = br.readLine()) != null) {
                if (line.trim().length() > 5) lines.add(line.trim());
            }
        }
        try (PrintWriter pw = new PrintWriter(new FileWriter("output.txt"))) {
            for (String l : lines) pw.println(l);
        }
        System.out.println(lines.size());
    }
}
