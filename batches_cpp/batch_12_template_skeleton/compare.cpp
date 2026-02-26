#include <iostream>
#include <fstream>
#include <string>
#include <algorithm>
using namespace std;

string transform(const string& s) {
    string result = s;
    for (char& c : result) c = toupper(c);
    return result;
}

int main(int argc, char* argv[]) {
    if (argc < 3) { cerr << "Usage: prog input output" << endl; return 1; }
    ifstream in(argv[1]);
    string data((istreambuf_iterator<char>(in)), istreambuf_iterator<char>());
    ofstream out(argv[2]);
    out << transform(data);
    return 0;
}
