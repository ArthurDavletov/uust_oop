#include <iostream>
#include <windows.h>

#include "point.h"
#include "segment.h"
#include "square.h"
#include "circle.h"

void PointCheck() {
  Point* point = new Point(1, 2);
  delete point;
}

void SegmentCheck() {
  Segment* segment = new Segment(1, 2, 3, 4);
  delete segment;
}

void SquareCheck() {
  Square* square = new Square(Point(1, 2), 3);
  delete square;
}

void CircleCheck() {
  Circle* circle = new Circle(Point(1, 2), 3);
  delete circle;
} 

int main() {
  // Исправление русского языка в консоли Windows
  SetConsoleCP(CP_UTF8);
  SetConsoleOutputCP(CP_UTF8);
  std::cout << "==========\n";
  PointCheck();
  std::cout << "==========\n";
  SegmentCheck();
  std::cout << "==========\n";
  SquareCheck();
  std::cout << "==========\n";
  CircleCheck();
  std::cout << "==========\n";
  std::cout << "Hello World! Привет, мир!" << std::endl;
}