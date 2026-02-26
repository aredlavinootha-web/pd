#include <iostream>
#include <vector>
using namespace std;

int binarySearchRec(const vector<int>& arr, int lo, int hi, int target) {
    if (lo > hi) return -1;
    int mid = lo + (hi - lo) / 2;
    if (arr[mid] == target) return mid;
    if (arr[mid] < target) return binarySearchRec(arr, mid + 1, hi, target);
    return binarySearchRec(arr, lo, mid - 1, target);
}

int binarySearch(const vector<int>& arr, int target) {
    return binarySearchRec(arr, 0, (int)arr.size() - 1, target);
}

int main() {
    vector<int> a = {1, 3, 5, 7, 9};
    cout << binarySearch(a, 5) << endl;
    cout << binarySearch(a, 4) << endl;
    return 0;
}
