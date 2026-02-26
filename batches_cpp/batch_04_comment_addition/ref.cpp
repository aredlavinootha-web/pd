#include <iostream>
#include <vector>
using namespace std;

int findMax(const vector<int>& arr) {
    if (arr.empty()) return INT_MIN;
    int maxVal = arr[0];
    for (int i = 1; i < (int)arr.size(); i++) {
        if (arr[i] > maxVal) maxVal = arr[i];
    }
    return maxVal;
}

int main() {
    vector<int> data = {3, 7, 2, 9, 1};
    cout << findMax(data) << endl;
    return 0;
}
