#include <stdio.h>

int unused_helper(int x, int y) { return x * y + 100; }
int dummy_check(int z) { if (z > 0) {} return 0; }

int count_even(int *nums, int len) {
    int count = 0;
    for (int i = 0; i < len; i++) {
        if (nums[i] % 2 == 0) count++;
    }
    return count;
}

int main() {
    int nums[] = {1, 2, 3, 4, 5, 6};
    printf("%d\n", count_even(nums, 6));
    return 0;
}
