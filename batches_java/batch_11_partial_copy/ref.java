import java.io.*;
import java.util.*;

public class ProcessData {
    public static List<String> fetchFromFile(String path) throws IOException {
        List<String> lines = new ArrayList<>();
        try (BufferedReader br = new BufferedReader(new FileReader(path))) {
            String line;
            while ((line = br.readLine()) != null) lines.add(line);
        }
        return lines;
    }

    public static void saveResults(List<String> items, String path) throws IOException {
        try (PrintWriter pw = new PrintWriter(new FileWriter(path))) {
            for (String item : items) pw.println(item.trim());
        }
    }

    public static int processData() throws IOException {
        List<String> data = fetchFromFile("input.txt");
        List<String> filtered = new ArrayList<>();
        for (String x : data) { if (x.trim().length() > 5) filtered.add(x.trim()); }
        saveResults(filtered, "output.txt");
        return filtered.size();
    }

    public static void main(String[] args) throws IOException {
        System.out.println(processData());
    }
}
