#include <cctype>
#include <cstring>
#include <iostream>
#include <string>
#include <vector>
using namespace std;

bool comparing_letters(char a, char b) {
  if ((isupper(a) && islower(b)) || (isupper(b) && islower(a))) {
    if (tolower(a) == tolower(b)) {
      return 1;
    }
  }
  return 0;
}

int main() {
  string s;
  cin >> s;

  int n;
  n = s.length();

  vector<int> orders(n / 2);

  vector<pair<char, int>> traps_and_animals;

  int counts_animals = 1;
  int counts_traps = 1;

  for (int i = 0; i < n; i++) {
    if (!traps_and_animals.empty() && comparing_letters(s[i], traps_and_animals.back().first)) {
      if (isupper(s[i])) {
        orders[counts_traps - 1] = traps_and_animals.back().second;
        counts_traps++;
      } else {
        orders[traps_and_animals.back().second - 1] = counts_animals;
        counts_animals++;
      }
      traps_and_animals.pop_back();
    } else {
      if (islower(s[i])) {
        traps_and_animals.push_back({s[i], counts_animals});
        counts_animals++;
      } else {
        traps_and_animals.push_back({s[i], counts_traps});
        counts_traps++;
      }
    }
  }
  if (!traps_and_animals.empty()) {
    cout << "Impossible";
  } else {
    cout << "Possible" << endl;
    for (int i = 0; i < n / 2; i++) {
      if (i == n / 2 - 1) {
        cout << orders[i];
      } else {
        cout << orders[i] << " ";
      }
    }
    cout << endl;
  }
  return 0;
}