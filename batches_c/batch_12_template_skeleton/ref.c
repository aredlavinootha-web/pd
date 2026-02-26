#include <stdio.h>
#include <ctype.h>

int main(int argc, char *argv[]) {
    if (argc < 3) { fprintf(stderr, "Usage: prog input output\n"); return 1; }
    FILE *in = fopen(argv[1], "r"), *out = fopen(argv[2], "w");
    char buf[4096]; size_t n;
    while ((n = fread(buf, 1, sizeof(buf), in)) > 0) {
        for (int i = 0; i < n; i++) buf[i] = toupper(buf[i]);
        fwrite(buf, 1, n, out);
    }
    fclose(in); fclose(out);
    return 0;
}
