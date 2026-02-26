#include <stdio.h>
#include <string.h>

int main() {
    FILE *in = fopen("input.txt", "r"), *out = fopen("output.txt", "w");
    char line[256]; int count = 0;
    while (fgets(line, 256, in)) {
        if (strlen(line) > 5) { fputs(line, out); count++; }
    }
    fclose(in); fclose(out);
    printf("%d\n", count);
    return 0;
}
