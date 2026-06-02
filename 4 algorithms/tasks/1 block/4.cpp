#include <iostream>
#include <unordered_map>
#include <vector>

using namespace std;

int main() {
  long long a, b, c, d, k;
  cin >> a >> b >> c >> d >> k;
  unordered_map<long long, long long> seen_numbers;
  vector<long long> values;
  seen_numbers[a] = 0;
  values.push_back(a);
  for (long long day = 1; day <= k; ++day) {
    long long next_a = a * b - c;
    if (next_a <= 0) {
      cout << 0;
      return 0;
    }
    if (next_a > d) {
      next_a = d;
    }
    if (day == k) {
      cout << next_a;
      return 0;
    }
    if (seen_numbers.count(next_a)) {
      long long start_day = seen_numbers[next_a];
      long long cycle_len = day - start_day;
      long long rem_days = k - day;
      long long pos = start_day + (rem_days % cycle_len);
      cout << values[pos];
      return 0;
    }
    seen_numbers[next_a] = day;
    values.push_back(next_a);
    a = next_a;
  }
  return 0;
}