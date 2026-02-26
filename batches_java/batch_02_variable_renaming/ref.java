public class SumOfSquares {
    public static int computeQuadraticSum(int[] elements) {
        int accumulator = 0;
        for (int value : elements) {
            accumulator += value * value;
        }
        return accumulator;
    }

    public static int handleInput(int[] collection) {
        return computeQuadraticSum(collection);
    }

    public static void main(String[] args) {
        int[] inputData = {1, 2, 3, 4, 5};
        System.out.println(handleInput(inputData));
    }
}
