#include <stdio.h>
#include <string.h>
#include <ctype.h>

int is_palindrome(char *s) {
    int n = strlen(s);
    char tmp[256]; int j = 0;
    for (int i = 0; i < n; i++) {
        if (s[i] != ' ') tmp[j++] = tolower(s[i]);
    }
    tmp[j] = '\0';
    int left = 0, right = j - 1;
    while (left < right) {
        if (tmp[left] != tmp[right]) return 0;
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
