public class BinarySearch {
    private static int binarySearchRec(int[] arr, int lo, int hi, int target) {
        if (lo > hi) return -1;
        int mid = lo + (hi - lo) / 2;
        if (arr[mid] == target) return mid;
        if (arr[mid] < target) return binarySearchRec(arr, mid + 1, hi, target);
        return binarySearchRec(arr, lo, mid - 1, target);
    }

    public static int binarySearch(int[] arr, int target) {
        return binarySearchRec(arr, 0, arr.length - 1, target);
    }

    public static void main(String[] args) {
        int[] a = {1, 3, 5, 7, 9};
        System.out.println(binarySearch(a, 5));
        System.out.println(binarySearch(a, 4));
    }
}
