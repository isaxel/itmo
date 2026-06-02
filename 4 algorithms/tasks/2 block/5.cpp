#include <algorithm>
#include <iostream>
#include <vector>

using namespace std;

int n, k;
vector<int> stalls;

bool check(int dist) {
  int count = 1;
  int last_pos = stalls[0];

  for (int i = 1; i < n; ++i) {
    if (stalls[i] - last_pos >= dist) {
      count++;
      last_pos = stalls[i];
    }
  }

  return count >= k;
}

int main() {
  if (!(cin >> n >> k))
    return 0;

  stalls.resize(n);
  for (int i = 0; i < n; ++i) {
    cin >> stalls[i];
  }

  int l = 0;
  int r = stalls[n - 1] - stalls[0];
  int ans = 0;

  while (l <= r) {
    int mid = l + (r - l) / 2;
    if (check(mid)) {
      ans = mid;
      l = mid + 1;
    } else {
      r = mid - 1;
    }
  }

  cout << ans << endl;

  return 0;
}