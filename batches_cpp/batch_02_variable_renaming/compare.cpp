#include <iostream>
#include <vector>
using namespace std;

int computeQuadraticSum(const vector<int>& elements) {
    int accumulator = 0;
    for (int value : elements) {
        accumulator += value * value;
    }
    return accumulator;
}

int handleInput(const vector<int>& collection) {
    return computeQuadraticSum(collection);
}

int main() {
    vector<int> inputData = {1, 2, 3, 4, 5};
    cout << handleInput(inputData) << endl;
    return 0;
}
