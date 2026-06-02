#include <iostream>
#include <map>
#include <set>
#include <vector>
using namespace std;

struct AllocResult {
  long long start;
  long long size;
  bool success;
};

map<long long, long long> by_start;
map<long long, long long> by_end;
set<pair<long long, long long>> free_set;
map<int, AllocResult> history;

void add_free_block(long long start, long long size) {
  long long end = start + size - 1;

  auto left = by_end.find(start - 1);
  if (left != by_end.end()) {
    long long l_start = left->second;
    long long l_size = by_start[l_start];
    free_set.erase({l_size, l_start});
    by_start.erase(l_start);
    by_end.erase(l_start + l_size - 1);
    start = l_start;
    size += l_size;
    end = start + size - 1;
  }

  auto right = by_start.find(end + 1);
  if (right != by_start.end()) {
    long long r_start = right->first;
    long long r_size = right->second;
    free_set.erase({r_size, r_start});
    by_start.erase(r_start);
    by_end.erase(r_start + r_size - 1);
    size += r_size;
  }

  free_set.insert({size, start});
  by_start[start] = size;
  by_end[start + size - 1] = start;
}

long long alloc(long long k) {
  auto it = free_set.lower_bound({k, 0});
  if (it == free_set.end())
    return -1;
  long long size = it->first;
  long long start = it->second;
  free_set.erase(it);
  by_start.erase(start);
  by_end.erase(start + size - 1);
  if (size > k) {
    add_free_block(start + k, size - k);
  }
  return start;
}

void free_by_request(int t) {
  if (!history[t].success)
    return;
  add_free_block(history[t].start, history[t].size);
}

int main() {
  long long n;
  int m;
  cin >> n >> m;
  add_free_block(1, n);
  for (int i = 1; i <= m; ++i) {
    long long x;
    cin >> x;
    if (x > 0) {
      long long res = alloc(x);
      cout << res << '\n';
      history[i] = {res, x, res != -1};
    } else {
      free_by_request((int)(-x));
    }
  }
  return 0;
}