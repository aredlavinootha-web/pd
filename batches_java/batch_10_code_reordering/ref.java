public class Stats {
    public static double[] computeStats(int[] data) {
        int n = data.length;
        int mx = data[0], mn = data[0], total = 0;
        for (int v : data) {
            if (v > mx) mx = v;
            if (v < mn) mn = v;
            total += v;
        }
        double avg = n > 0 ? (double) total / n : 0;
        return new double[]{avg, mx, mn};
    }

    public static void main(String[] args) {
        int[] d = {10, 20, 30, 40, 50};
        double[] result = computeStats(d);
        System.out.printf("avg=%.1f max=%.0f min=%.0f%n", result[0], result[1], result[2]);
    }
}
