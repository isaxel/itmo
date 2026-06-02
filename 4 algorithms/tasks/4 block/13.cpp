#include <algorithm>
#include <climits>
#include <deque>
#include <iostream>
#include <vector>

using namespace std;

void print_result(int dist_val, const string &path) {
  if (dist_val == INT_MAX) {
    cout << -1 << endl;
  } else {
    cout << dist_val << "\n" << path;
  }
}

int main() {
  int N, M;
  cin >> N >> M;

  int x1, y1, x2, y2;
  cin >> x1 >> y1 >> x2 >> y2;
  x1--;
  y1--;
  x2--;
  y2--;

  vector<string> grid(N);
  for (int i = 0; i < N; i++)
    cin >> grid[i];

  vector<vector<int>> dist(N, vector<int>(M, INT_MAX));
  vector<vector<pair<int, int>>> prev(N, vector<pair<int, int>>(M, {-1, -1}));
  vector<vector<char>> dir(N, vector<char>(M, 0));

  int dx[] = {-1, 0, 1, 0};
  int dy[] = {0, 1, 0, -1};
  char dc[] = {'N', 'E', 'S', 'W'};

  dist[x1][y1] = 0;
  deque<pair<int, int>> dq;
  dq.push_back({x1, y1});

  while (!dq.empty()) {
    auto [x, y] = dq.front();
    dq.pop_front();

    for (int d = 0; d < 4; d++) {
      int n1 = x + dx[d];
      int n2 = y + dy[d];

      if (n1 < 0 || n1 >= N || n2 < 0 || n2 >= M)
        continue;
      if (grid[n1][n2] == '#')
        continue;

      int w = (grid[n1][n2] == 'W') ? 2 : 1;
      int nd = dist[x][y] + w;

      if (nd < dist[n1][n2]) {
        dist[n1][n2] = nd;
        prev[n1][n2] = {x, y};
        dir[n1][n2] = dc[d];

        if (w == 1)
          dq.push_back({n1, n2});
        else
          dq.push_front({n1, n2});
      }
    }
  }

  string path;
  int x = x2, y = y2;
  while (x != x1 || y != y1) {
    path += dir[x][y];
    auto [p1, p2] = prev[x][y];
    x = p1;
    y = p2;
  }
  reverse(path.begin(), path.end());

  print_result(dist[x2][y2], path);

  return 0;
}