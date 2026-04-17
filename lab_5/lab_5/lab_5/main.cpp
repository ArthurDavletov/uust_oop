#include <iostream>
#include <windows.h>

int main() {
  // Исправление русского языка в консоли Windows
  SetConsoleCP(CP_UTF8);
  SetConsoleOutputCP(CP_UTF8);
  std::cout << "Привет, мир!" << std::endl;
  return 0;
}
