#include <iostream>
#include <vector>
using namespace std;

void swap(int& a, int& b) { int t = a; a = b; b = t; }

int partition(vector<int>& arr, int lo, int hi) {
    int pivot = arr[hi], i = lo - 1;
    for (int j = lo; j < hi; j++) {
        if (arr[j] <= pivot) { i++; swap(arr[i], arr[j]); }
    }
    swap(arr[i + 1], arr[hi]);
    return i + 1;
}

void quickSort(vector<int>& arr, int lo, int hi) {
    if (lo < hi) {
        int p = partition(arr, lo, hi);
        quickSort(arr, lo, p - 1);
        quickSort(arr, p + 1, hi);
    }
}

int main() {
    vector<int> data = {64, 34, 25, 12, 22, 11, 90};
    quickSort(data, 0, (int)data.size() - 1);
    for (int x : data) cout << x << " ";
    cout << endl;
    return 0;
}
