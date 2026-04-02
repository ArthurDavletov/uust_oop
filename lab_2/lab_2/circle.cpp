#include "circle.h"
#include <iostream>
#include <string>
#include <format>
#include <utility>
#include <numbers>
#include "point.h"

Circle::Circle() {
  std::cout << "Вызван конструктор по умолчанию для Circle\n";
}

Circle::Circle(const Point& center, double radius) : center_(center), radius_(radius) {
  std::cout << "Вызван конструктор с параметрами для Circle\n";
}

Circle::Circle(const Circle& other) : center_(other.center_), radius_(other.radius_) {
  std::cout << "Вызван конструктор копирования для Circle\n";
}

Circle::Circle(Circle&& other) noexcept : center_(std::move(other.center_)), radius_(other.radius_) {
  std::cout << "Вызван конструктор перемещения для Circle\n";
}

Circle::~Circle() {
  std::cout << "Вызван деструктор для Circle\n";
}

double Circle::Area() const {
  std::cout << "Вызван метод Area для Circle\n";
  return std::numbers::pi * radius_ * radius_;
}

double Circle::Perimeter() const {
  std::cout << "Вызван метод Perimeter для Circle\n";
  return 2 * std::numbers::pi * radius_;
}

std::string Circle::ToString() const {
  std::cout << "Вызван метод ToString для Circle\n";
  return std::format("Circle({}, {})", center_.ToString(), radius_);
}