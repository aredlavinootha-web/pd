#include <stdio.h>

int find_max(int *arr, int len) {
    if (len == 0) return -1;
    int max_val = arr[0];
    for (int i = 1; i < len; i++) {
        if (arr[i] > max_val) max_val = arr[i];
    }
    return max_val;
}

int main() {
    int data[] = {3, 7, 2, 9, 1};
    printf("%d\n", find_max(data, 5));
    return 0;
}
