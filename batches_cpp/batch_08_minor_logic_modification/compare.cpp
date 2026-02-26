#include <iostream>
using namespace std;

int maxOfTwo(int a, int b) {
    if (a > b) return a;
    return b;
}

int main() {
    cout << maxOfTwo(3, 7) << endl;
    cout << maxOfTwo(10, 5) << endl;
    return 0;
}
