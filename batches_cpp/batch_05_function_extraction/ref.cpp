#include <iostream>
#include <string>
#include <algorithm>
using namespace std;

string normalize(string s) {
    transform(s.begin(), s.end(), s.begin(), ::tolower);
    s.erase(remove(s.begin(), s.end(), ' '), s.end());
    return s;
}

bool charsMatch(const string& s, int l, int r) {
    return s[l] == s[r];
}

bool isPalindrome(string s) {
    s = normalize(s);
    int left = 0, right = (int)s.size() - 1;
    while (left < right) {
        if (!charsMatch(s, left, right)) return false;
        left++; right--;
    }
    return true;
}

int main() {
    cout << isPalindrome("amanaplanacanalpanama") << endl;
    cout << isPalindrome("hello") << endl;
    return 0;
}
