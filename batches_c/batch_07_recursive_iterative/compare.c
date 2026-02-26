#include <stdio.h>

int factorial(int n) {
    int result = 1;
    for (int i = 2; i <= n; i++) result *= i;
    return result;
}

int main() {
    printf("%d\n%d\n", factorial(5), factorial(0));
    return 0;
}
