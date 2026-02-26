// Method to find the maximum value in an array
public class FindMax {
    // Returns the maximum value
    public static int findMax(int[] arr) {
        // Handle empty array
        if (arr == null || arr.length == 0) return Integer.MIN_VALUE;
        // Start with first element
        int maxVal = arr[0];
        // Iterate through remaining elements
        for (int i = 1; i < arr.length; i++) {
            // Update if larger value found
            if (arr[i] > maxVal) maxVal = arr[i];
        }
        return maxVal;
    }

    // Entry point
    public static void main(String[] args) {
        int[] data = {3, 7, 2, 9, 1};
        System.out.println(findMax(data));
    }
}
