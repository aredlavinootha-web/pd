#include <iostream>
#include <fstream>
#include <vector>
#include <string>
using namespace std;

vector<string> fetchLines(const string& path) {
    ifstream f(path);
    vector<string> lines;
    string line;
    while (getline(f, line)) lines.push_back(line);
    return lines;
}

void saveResults(const vector<string>& items, const string& path) {
    ofstream f(path);
    for (const auto& s : items) f << s << "\n";
}

int processData() {
    auto data = fetchLines("input.txt");
    vector<string> filtered;
    for (auto& x : data) if (x.size() > 5) filtered.push_back(x);
    saveResults(filtered, "output.txt");
    return filtered.size();
}

int main() {
    cout << processData() << endl;
    return 0;
}
