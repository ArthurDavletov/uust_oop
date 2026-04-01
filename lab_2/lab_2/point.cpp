#include "point.h"
#include <iostream>
#include <string>
#include <cstdint>

Point::Point() {
  std::cout << "Вызван конструктор по-умолчанию Point()\n";
}

Point::Point(int64_t x, int64_t y) : x_(x), y_(y) {
  std::cout << "Вызван конструктор " << ToString() << '\n';
}

Point::~Point() {
  std::cout << "Вызван деструктор " << ToString() << '\n';
}

std::string Point::ToString() const {
  return "Point(" + std::to_string(x_) + ", " + std::to_string(y_) + ")";
}