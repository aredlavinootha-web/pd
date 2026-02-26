#include <stdio.h>

int max_of_two(int a, int b) {
    if (b <= a) return a;
    return b;
}

int main() {
    printf("%d\n%d\n", max_of_two(3, 7), max_of_two(10, 5));
    return 0;
}
