#include <iostream>
#include <vector>
using namespace std;

void selectionSort(vector<int>& arr) {
    for (int i = 0; i < (int)arr.size(); i++) {
        int minIdx = i;
        for (int j = i + 1; j < (int)arr.size(); j++) {
            if (arr[j] < arr[minIdx]) minIdx = j;
        }
        int tmp = arr[i]; arr[i] = arr[minIdx]; arr[minIdx] = tmp;
    }
}

int main() {
    vector<int> data = {64, 34, 25, 12, 22, 11, 90};
    selectionSort(data);
    for (int x : data) cout << x << " ";
    cout << endl;
    return 0;
}
