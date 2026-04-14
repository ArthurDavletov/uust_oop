#include "point.h"
#include <iostream>
#include <string>
#include <format>

Point::Point() {
  std::cout << "[DEBUG] Вызван конструктор по умолчанию Point\n";
}

Point::Point(double x, double y) : x_(x), y_(y) {
  std::cout << "[DEBUG] Вызван конструктор с параметрами Point\n";
}

Point::Point(const Point& other) : x_(other.GetX()), y_(other.GetY()) {
  std::cout << "[DEBUG] Вызван конструктор копирования Point\n";
}

Point::Point(Point&& other) noexcept : x_(other.GetX()), y_(other.GetY()) {
  std::cout << "[DEBUG] Вызван конструктор перемещения Point\n";
}

std::string Point::Description() const {
  std::cout << "[DEBUG] Вызван метод Description для Point\n";
  return std::format("Это Point с координатами ({}, {})", x_, y_);
}

void Point::SetX(double x) {
  std::cout << "[DEBUG] Вызван метод SetX для Point\n";
  x_ = x;
}

void Point::SetY(double y) {
  std::cout << "[DEBUG] Вызван метод SetY для Point\n";
  y_ = y;
}

void Point::SetXY(double x, double y) {
  std::cout << "[DEBUG] Вызван метод SetXY для Point\n";
  x_ = x;
  y_ = y;
}

Point::~Point() {
  std::cout << "[DEBUG] Вызван деструктор Point\n";
}

std::string Point::ToString() const {
  std::cout << "[DEBUG] Вызван метод ToString для Point\n";
  return std::format("Point({}, {})", x_, y_);
}