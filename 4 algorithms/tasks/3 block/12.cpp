#include <algorithm>
#include <iostream>
#include <set>
#include <vector>

using namespace std;

int main() {
  int n, k;
  cin >> n >> k;
  vector<int> numbers(n);
  for (int i = 0; i < n; i++) {
    cin >> numbers[i];
  }
  multiset<int> k_numbers;
  for (int i = 0; i < n; i++) {
    if (i < k - 1) {
      k_numbers.insert(numbers[i]);
    } else {
      if (i != k - 1) {
        k_numbers.erase(k_numbers.find(numbers[i - k]));
      }
      k_numbers.insert(numbers[i]);
      cout << *k_numbers.begin() << " ";
    }
  }
  return 0;
}