#include "point.h"
#include <iostream>
#include <string>
#include <format>

Point::Point() {
  std::cout << "Вызван конструктор по умолчанию Point\n";
}

Point::Point(double x, double y) : x_(x), y_(y) {
  std::cout << "Вызван конструктор Point\n";
}

Point::Point(const Point& other) : x_(other.GetX()), y_(other.GetY()) {
  std::cout << "Вызван конструктор копирования Point\n";
}

Point::Point(Point&& other) noexcept : x_(other.GetX()), y_(other.GetY()) {
  std::cout << "Вызван конструктор перемещения Point\n";
}

Point::~Point() {
  std::cout << "Вызван деструктор Point\n";
}

std::string Point::ToString() const {
  std::cout << "Вызван метод ToString для Point\n";
  return std::format("Point({}, {})", x_, y_);
}