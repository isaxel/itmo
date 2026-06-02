#include <algorithm>
#include <iostream>
#include <set>
#include <vector>

using namespace std;

int n, k, p;

vector<int> needed_cars;
vector<vector<int>> needed_cars_positions;
set<pair<int, int>> floor_cars;
vector<int> car_next_use;

int find_next_use(int car, int current) {
  vector<int>& vec = needed_cars_positions[car];
  auto it = upper_bound(vec.begin(), vec.end(), current);
  if (it == vec.end())
    return p + 1;
  return vec[it - vec.begin()];
}

bool is_on_floor(int car) {
  return car_next_use[car] != -1;
}

void remove_from_floor(int car) {
  floor_cars.erase({car_next_use[car], car});
  car_next_use[car] = -1;
}

void add_to_floor(int car, int step) {
  int next = find_next_use(car, step);
  floor_cars.insert({next, car});
  car_next_use[car] = next;
}

void evict_worst() {
  int victim = prev(floor_cars.end())->second;
  remove_from_floor(victim);
}

void refresh_on_floor(int car, int step) {
  remove_from_floor(car);
  add_to_floor(car, step);
}

int main() {
  cin >> n >> k >> p;
  needed_cars.resize(p);
  needed_cars_positions.resize(n + 1);
  car_next_use.assign(n + 1, -1);

  for (int i = 0; i < p; i++) {
    cin >> needed_cars[i];
    needed_cars_positions[needed_cars[i]].push_back(i);
  }

  int count_operations = 0;
  for (int i = 0; i < p; i++) {
    int car = needed_cars[i];
    if (is_on_floor(car)) {
      refresh_on_floor(car, i);
    } else {
      count_operations++;
      if ((int)floor_cars.size() == k) {
        evict_worst();
      }
      add_to_floor(car, i);
    }
  }
  cout << count_operations;
  return 0;
}