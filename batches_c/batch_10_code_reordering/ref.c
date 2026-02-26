#include <stdio.h>

void compute_stats(int *data, int len, double *avg, int *mx, int *mn) {
    *mx = data[0]; *mn = data[0];
    int total = 0;
    for (int i = 0; i < len; i++) {
        if (data[i] > *mx) *mx = data[i];
        if (data[i] < *mn) *mn = data[i];
        total += data[i];
    }
    *avg = len > 0 ? (double)total / len : 0;
}

int main() {
    int d[] = {10, 20, 30, 40, 50};
    double avg; int mx, mn;
    compute_stats(d, 5, &avg, &mx, &mn);
    printf("avg=%.1f max=%d min=%d\n", avg, mx, mn);
    return 0;
}
