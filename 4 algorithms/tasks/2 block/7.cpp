#include <algorithm>
#include <iostream>
#include <string>
#include <vector>

using namespace std;

struct Letter {
  char symbol;
  long long value;
};

bool compare(const Letter& a, const Letter& b) {
  return a.value > b.value;
}

int main() {
  string s;
  if (!(cin >> s))
    return 0;

  int n = s.length();
  vector<long long> weights(26);
  for (int i = 0; i < 26; ++i) {
    cin >> weights[i];
  }

  vector<int> counts(26, 0);
  for (char c : s) {
    counts[c - 'a']++;
  }

  vector<Letter> pairs;
  for (int i = 0; i < 26; ++i) {
    if (counts[i] >= 2) {
      pairs.push_back({(char)('a' + i), weights[i]});
    }
  }

  sort(pairs.begin(), pairs.end(), compare);

  string res(n, ' ');
  vector<bool> fixed(n, false);
  int L = 0;
  int R = n - 1;

  for (const auto& item : pairs) {
    if (L >= R)
      break;

    res[L] = item.symbol;
    res[R] = item.symbol;
    fixed[L] = true;
    fixed[R] = true;

    counts[item.symbol - 'a'] -= 2;

    L++;
    R--;
  }

  int idx = 0;
  for (int i = 0; i < n; ++i) {
    if (!fixed[i]) {
      while (idx < 26 && counts[idx] == 0) {
        idx++;
      }
      if (idx < 26) {
        res[i] = (char)('a' + idx);
        counts[idx]--;
      }
    }
  }

  cout << res << endl;

  return 0;
}