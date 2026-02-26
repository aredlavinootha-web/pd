#include <stdio.h>

int compute_quadratic_sum(int *elements, int len) {
    int accumulator = 0;
    for (int i = 0; i < len; i++) {
        accumulator += elements[i] * elements[i];
    }
    return accumulator;
}

int main() {
    int input_data[] = {1, 2, 3, 4, 5};
    printf("%d\n", compute_quadratic_sum(input_data, 5));
    return 0;
}
