#include <stdio.h>
#include <string.h>

void read_lines(const char *path, char lines[][256], int *count) {
    FILE *f = fopen(path, "r");
    *count = 0;
    while (fgets(lines[(*count)], 256, f)) (*count)++;
    fclose(f);
}

void save_results(char lines[][256], int count, const char *path) {
    FILE *f = fopen(path, "w");
    for (int i = 0; i < count; i++) fprintf(f, "%s", lines[i]);
    fclose(f);
}

int process_data() {
    char data[100][256]; int n;
    read_lines("input.txt", data, &n);
    char filtered[100][256]; int k = 0;
    for (int i = 0; i < n; i++) {
        if (strlen(data[i]) > 5) { strcpy(filtered[k++], data[i]); }
    }
    save_results(filtered, k, "output.txt");
    return k;
}

int main() { printf("%d\n", process_data()); return 0; }
