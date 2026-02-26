#include <stdio.h>
#include <string.h>
#include <ctype.h>

void normalize(char *s) {
    int j = 0;
    for (int i = 0; s[i]; i++) {
        if (s[i] != ' ') s[j++] = tolower(s[i]);
    }
    s[j] = '\0';
}

int chars_match(const char *s, int l, int r) {
    return s[l] == s[r];
}

int is_palindrome(char *s) {
    normalize(s);
    int left = 0, right = strlen(s) - 1;
    while (left < right) {
        if (!chars_match(s, left, right)) return 0;
        left++; right--;
    }
    return 1;
}

int main() {
    char s1[] = "amanaplanacanalpanama";
    char s2[] = "hello";
    printf("%d\n%d\n", is_palindrome(s1), is_palindrome(s2));
    return 0;
}
