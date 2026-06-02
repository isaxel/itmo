#include <cstring>
#include <iostream>
#include <string>

int main() {
  int t;
  std::string line;

  std::cin >> t;

  for (int i = 0; i < t; i++) {
    std::cin >> line;
    if (line.length() % 2 == 0) {
      if (line.substr(0, line.length() / 2) ==
          line.substr(line.length() / 2, line.length() / 2)) {
        std::cout << "YES\n";
      } else {
        std::cout << "NO\n";
      }
    } else {
      std::cout << "NO\n";
    }
  }
  return 0;
}