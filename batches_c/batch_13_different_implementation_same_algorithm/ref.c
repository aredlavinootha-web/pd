#include <stdio.h>

int binary_search(int *arr, int len, int target) {
    int left = 0, right = len - 1;
    while (left <= right) {
        int center = left + (right - left) / 2;
        if (arr[center] == target) return center;
        if (arr[center] < target) left = center + 1;
        else right = center - 1;
    }
    return -1;
}

int main() {
    int a[] = {1, 3, 5, 7, 9};
    printf("%d\n%d\n", binary_search(a, 5, 5), binary_search(a, 5, 4));
    return 0;
}
