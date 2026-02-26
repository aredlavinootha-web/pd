public class BinarySearch {
    public static int binarySearch(int[] arr, int target) {
        int left = 0, right = arr.length - 1;
        while (left <= right) {
            int center = left + (right - left) / 2;
            int val = arr[center];
            if (val == target) return center;
            if (val < target) left = center + 1;
            else right = center - 1;
        }
        return -1;
    }

    public static void main(String[] args) {
        int[] a = {1, 3, 5, 7, 9};
        System.out.println(binarySearch(a, 5));
        System.out.println(binarySearch(a, 4));
    }
}
