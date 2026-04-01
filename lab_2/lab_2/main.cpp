#include <iostream>
#include <windows.h>

#include "point.h"
#include "segment.h"

void PointCheck() {
  Point* point = new Point(1, 2);
  delete point;
}

void SegmentCheck() {
  Segment* segment = new Segment(1, 2, 3, 4);
  delete segment;
}

int main() {
  // Исправление русского языка в консоли Windows
  SetConsoleCP(CP_UTF8);
  SetConsoleOutputCP(CP_UTF8);
  PointCheck();
  std::cout << "==========\n";
  SegmentCheck();

  std::cout << "Hello World!\n";
  std::cout << "Привет, мир!\n";
  std::cout << std::endl;
}