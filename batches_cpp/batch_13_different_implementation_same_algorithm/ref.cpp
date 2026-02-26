#include <iostream>
#include <vector>
using namespace std;

int binarySearch(const vector<int>& arr, int target) {
    int left = 0, right = (int)arr.size() - 1;
    while (left <= right) {
        int center = left + (right - left) / 2;
        if (arr[center] == target) return center;
        if (arr[center] < target) left = center + 1;
        else right = center - 1;
    }
    return -1;
}

int main() {
    vector<int> a = {1, 3, 5, 7, 9};
    cout << binarySearch(a, 5) << endl;
    cout << binarySearch(a, 4) << endl;
    return 0;
}
