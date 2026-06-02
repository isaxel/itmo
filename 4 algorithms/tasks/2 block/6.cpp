#include <algorithm>
#include <iostream>
#include <string>
#include <vector>

using namespace std;

bool compareFragments(const string& a, const string& b) {
  return a + b > b + a;
}

int main() {
  vector<string> fragments;
  string s;

  while (cin >> s) {
    fragments.push_back(s);
  }

  sort(fragments.begin(), fragments.end(), compareFragments);

  for (const string& fragment : fragments) {
    cout << fragment;
  }