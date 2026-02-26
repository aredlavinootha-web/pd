#include <iostream>
#include <vector>
using namespace std;

int sumList(const vector<int>& nums) {
    int total = 0;
    for (int n : nums) total += n;
    return total;
}

int main() {
    vector<int> nums = {1, 2, 3, 4, 5};
    cout << sumList(nums) << endl;
    return 0;
}
