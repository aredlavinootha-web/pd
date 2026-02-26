#include <iostream>
#include <vector>
using namespace std;

int unusedHelper(int x, int y) { return x * y + 100; }
bool dummyCheck(int z) { if (z > 0) {} return false; }

int countEven(const vector<int>& nums) {
    int count = 0;
    for (int n : nums) if (n % 2 == 0) count++;
    return count;
}

int main() {
    vector<int> nums = {1, 2, 3, 4, 5, 6};
    cout << countEven(nums) << endl;
    return 0;
}
