public class MaxOfTwo {
    public static int maxOfTwo(int a, int b) {
        if (a > b) return a;
        return b;
    }

    public static void main(String[] args) {
        System.out.println(maxOfTwo(3, 7));
        System.out.println(maxOfTwo(10, 5));
    }
}
