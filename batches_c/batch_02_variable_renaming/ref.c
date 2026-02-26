#include <stdio.h>

int sum_of_squares(int *numbers, int size) {
    int total = 0;
    for (int j = 0; j < size; j++) {
        total += numbers[j] * numbers[j];
    }
    return total;
}

int main() {
    int my_list[] = {1, 2, 3, 4, 5};
    printf("%d\n", sum_of_squares(my_list, 5));
    return 0;
}
