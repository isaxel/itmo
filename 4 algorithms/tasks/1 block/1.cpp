#include <cstring>
#include <iostream>
#include <string>
using namespace std;

int main() {
  int n;
  int ai, ai1, ai2;
  int first_index_max = 1, last_index_max = 1;
  int first_index_current = 1, last_index_current = 1;

  cin >> n;
  cin >> ai >> ai1;

  for (int i = 3; i <= n; i++) {
    cin >> ai2;

    if (ai2 == ai1 && ai2 == ai) {
      last_index_current = i - 1;

      if (last_index_current - first_index_current > last_index_max - first_index_max) {
        last_index_max = last_index_current;
        first_index_max = first_index_current;
      }
      first_index_current = i - 1;
    }
    ai = ai1;
    ai1 = ai2;
  }

  if (n - first_index_current > last_index_max - first_index_max) {
    cout << first_index_current << " " << n;
  } else {
    cout << first_index_max << " " << last_index_max;
  }

  return 0;
}