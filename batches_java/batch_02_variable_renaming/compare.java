public class SumOfSquares {
    public static int sumOfSquares(int[] numbers) {
        int total = 0;
        for (int num : numbers) {
            total += num * num;
        }
        return total;
    }

    public static int processList(int[] data) {
        return sumOfSquares(data);
    }

    public static void main(String[] args) {
        int[] myList = {1, 2, 3, 4, 5};
        System.out.println(processList(myList));
    }
}
