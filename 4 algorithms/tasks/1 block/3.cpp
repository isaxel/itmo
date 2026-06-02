#include <cctype>
#include <iostream>
#include <map>
#include <string>
#include <vector>

using namespace std;

bool is_number(string s) {
  if (s.empty())
    return false;
  return isdigit(s[0]) || s[0] == '-';
}

int main() {
  map<string, vector<int>> parameters;
  vector<vector<string>> blocks;
  blocks.push_back(vector<string>());

  string line;
  while (cin >> line) {
    if (line == "{") {
      blocks.push_back(vector<string>());
    } else if (line == "}") {
      vector<string> current_block = blocks.back();
      for (size_t i = 0; i < current_block.size(); i++) {
        string var_name = current_block[i];
        parameters[var_name].pop_back();
      }
      blocks.pop_back();
    } else {
      int eq_pos = line.find('=');
      string var1 = line.substr(0, eq_pos);
      string right_part = line.substr(eq_pos + 1);
      int val = 0;
      if (is_number(right_part)) {
        val = stoi(right_part);
      } else {
        if (!parameters[right_part].empty()) {
          val = parameters[right_part].back();
        }
        cout << val << "\n";
      }
      parameters[var1].push_back(val);
      blocks.back().push_back(var1);
    }
  }
  return 0;
}