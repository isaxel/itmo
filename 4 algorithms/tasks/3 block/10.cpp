#include <algorithm>
#include <iostream>
#include <set>
#include <vector>

using namespace std;

int main() {
  int n;
  string symbol;
  vector<int> goblin_queue;
  int goblin;
  int goblin_index;
  cin >> n;
  for (int i = 0; i < n; i++) {
    cin >> symbol;
    if (symbol == "-") {
      cout << goblin_queue[0] << "\n";
      goblin_queue.erase(goblin_queue.begin());
    }
    if (symbol == "*" || symbol == "+") {
      cin >> goblin;
      if (symbol == "*") {
        if (goblin_queue.size() % 2 == 0) {
          goblin_index = goblin_queue.size() / 2;
          goblin_queue.insert(goblin_queue.begin() + goblin_index, goblin);
        } else {
          goblin_index = goblin_queue.size() / 2 + 1;
          goblin_queue.insert(goblin_queue.begin() + goblin_index, goblin);
        }
      } else {
        goblin_queue.push_back(goblin);
      }
    }
  }
  return 0;
}