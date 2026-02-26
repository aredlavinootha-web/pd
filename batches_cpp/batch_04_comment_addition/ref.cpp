#include <iostream>
#include <vector>
using namespace std;

// Returns the maximum element in the array
int findMax(const vector<int>& arr) {
    // Handle empty input
    if (arr.empty()) return INT_MIN;
    // Start with first element
    int maxVal = arr[0];
    // Check each remaining element
    for (int i = 1; i < (int)arr.size(); i++) {
        // Update max if larger found
        if (arr[i] > maxVal) maxVal = arr[i];
    }
    return maxVal;
}

// Program entry point
int main() {
    vector<int> data = {3, 7, 2, 9, 1};
    cout << findMax(data) << endl;
    return 0;
}
