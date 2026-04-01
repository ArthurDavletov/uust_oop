#include <iostream>
#include <windows.h>

#include "point.h"


int main() {
  // Исправление русского языка в консоли Windows
  SetConsoleCP(CP_UTF8);
  SetConsoleOutputCP(CP_UTF8);

  Point* point = new Point(1, 2);
  std::cout << "Hello World!\n";
  std::cout << "Привет, мир!\n";
  delete point;
}