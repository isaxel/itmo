#include <algorithm>
#include <iostream>
#include <vector>

using namespace std;

int main() {
  int quantity, step;
  if (!(cin >> quantity >> step))
    return 0;

  vector<int> prices(quantity);
  long long total = 0;

  for (int i = 0; i < quantity; i++) {
    cin >> prices[i];
    total += prices[i];
  }

  sort(prices.begin(), prices.end(), greater<int>());

  long long discount = 0;
  for (int i = step - 1; i < quantity; i += step) {
    discount += prices[i];
  }

  cout << total - discount << endl;

  return 0;
}