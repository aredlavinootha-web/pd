#include <stdio.h>

int sum_list(int *nums, int len) {
    int total = 0;
    for (int i = 0; i < len; i++) { total += nums[i]; }
    return total;
}

int main() {
    int nums[] = {1, 2, 3, 4, 5};
    printf("%d\n", sum_list(nums, 5));
    return 0;
}
