public class FindMax {
    public static int findMax(int[] arr) {
        if (arr == null || arr.length == 0) return Integer.MIN_VALUE;
        int maxVal = arr[0];
        for (int i = 1; i < arr.length; i++) {
            if (arr[i] > maxVal) maxVal = arr[i];
        }
        return maxVal;
    }

    public static void main(String[] args) {
        int[] data = {3, 7, 2, 9, 1};
        System.out.println(findMax(data));
    }
}
