#include <stdio.h>

/* Find max value in array */
int find_max(int *arr, int len) {
    /* Handle edge case */
    if (len == 0) return -1;
    /* Initialize with first element */
    int max_val = arr[0];
    /* Traverse remaining elements */
    for (int i = 1; i < len; i++) {
        /* Update if larger found */
        if (arr[i] > max_val) max_val = arr[i];
    }
    return max_val;
}

/* Entry point */
int main() {
    int data[] = {3, 7, 2, 9, 1};
    printf("%d\n", find_max(data, 5));
    return 0;
}
