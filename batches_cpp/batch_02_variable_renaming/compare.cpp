#include <iostream>
#include <vector>
using namespace std;

int sumOfSquares(const vector<int>& numbers) {
    int total = 0;
    for (int num : numbers) {
        total += num * num;
    }
    return total;
}

int processList(const vector<int>& data) {
    return sumOfSquares(data);
}

int main() {
    vector<int> myList = {1, 2, 3, 4, 5};
    cout << processList(myList) << endl;
    return 0;
}
