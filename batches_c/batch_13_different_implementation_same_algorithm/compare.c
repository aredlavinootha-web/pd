#include <stdio.h>

int binary_search(int *arr, int len, int target) {
    int lo = 0, hi = len - 1;
    while (lo <= hi) {
        int mid = (lo + hi) / 2;
        if (arr[mid] == target) return mid;
        if (arr[mid] < target) lo = mid + 1;
        else hi = mid - 1;
    }
    return -1;
}

int main() {
    int a[] = {1, 3, 5, 7, 9};
    printf("%d\n%d\n", binary_search(a, 5, 5), binary_search(a, 5, 4));
    return 0;
}
