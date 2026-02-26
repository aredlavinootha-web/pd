#include <stdio.h>

int binary_search_rec(int *arr, int lo, int hi, int target) {
    if (lo > hi) return -1;
    int mid = lo + (hi - lo) / 2;
    if (arr[mid] == target) return mid;
    if (arr[mid] < target) return binary_search_rec(arr, mid + 1, hi, target);
    return binary_search_rec(arr, lo, mid - 1, target);
}

int binary_search(int *arr, int len, int target) {
    return binary_search_rec(arr, 0, len - 1, target);
}

int main() {
    int a[] = {1, 3, 5, 7, 9};
    printf("%d\n%d\n", binary_search(a, 5, 5), binary_search(a, 5, 4));
    return 0;
}
