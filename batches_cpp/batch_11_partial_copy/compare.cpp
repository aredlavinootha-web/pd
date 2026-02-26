#include <iostream>
#include <fstream>
#include <string>
using namespace std;

int main() {
    ifstream in("input.txt");
    ofstream out("output.txt");
    string line; int count = 0;
    while (getline(in, line)) {
        if (line.size() > 5) { out << line << "\n"; count++; }
    }
    cout << count << endl;
    return 0;
}
