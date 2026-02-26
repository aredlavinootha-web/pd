import java.util.*;

public class QuickSort {
    public static List<Integer> quickSort(List<Integer> arr) {
        if (arr.size() <= 1) return arr;
        int pivot = arr.get(arr.size() / 2);
        List<Integer> left = new ArrayList<>(), mid = new ArrayList<>(), right = new ArrayList<>();
        for (int x : arr) {
            if (x < pivot) left.add(x);
            else if (x == pivot) mid.add(x);
            else right.add(x);
        }
        List<Integer> result = quickSort(left);
        result.addAll(mid);
        result.addAll(quickSort(right));
        return result;
    }

    public static void main(String[] args) {
        List<Integer> data = new ArrayList<>(Arrays.asList(64, 34, 25, 12, 22, 11, 90));
        System.out.println(quickSort(data));
    }
}
