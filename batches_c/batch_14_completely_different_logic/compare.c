#include <stdio.h>

void selection_sort(int *arr, int len) {
    for (int i = 0; i < len; i++) {
        int min_idx = i;
        for (int j = i + 1; j < len; j++) {
            if (arr[j] < arr[min_idx]) min_idx = j;
        }
        int tmp = arr[i]; arr[i] = arr[min_idx]; arr[min_idx] = tmp;
    }
}

int main() {
    int data[] = {64, 34, 25, 12, 22, 11, 90};
    selection_sort(data, 7);
    for (int i = 0; i < 7; i++) printf("%d ", data[i]);
    printf("\n");
    return 0;
}
