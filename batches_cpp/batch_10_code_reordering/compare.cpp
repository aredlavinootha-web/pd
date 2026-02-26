#include <iostream>
#include <vector>
using namespace std;

void computeStats(const vector<int>& data, double& avg, int& mx, int& mn) {
    int total = 0;
    for (int v : data) total += v;
    avg = !data.empty() ? (double)total / data.size() : 0;
    mx = data[0]; mn = data[0];
    for (int v : data) {
        if (v > mx) mx = v;
        if (v < mn) mn = v;
    }
}

int main() {
    vector<int> d = {10, 20, 30, 40, 50};
    double avg; int mx, mn;
    computeStats(d, avg, mx, mn);
    cout << "avg=" << avg << " max=" << mx << " min=" << mn << endl;
    return 0;
}
