#include <iostream>
#include <format>
#include <string>
#include <utility>
#include "shape.h"
#include "square.h"
#include "point.h"

Square::Square() {
  std::cout << "Вызван конструктор по умолчанию для Square\n";
}

Square::Square(const Point& center, double side_length) : center_(center), side_length_(side_length) {
  std::cout << "Вызван конструктор с параметрами для Square\n";
}

Square::~Square() {
  std::cout << "Вызван деструктор для Square\n";
}

Square::Square(const Square& other) : center_(other.center_), side_length_(other.side_length_) {
  std::cout << "Вызван конструктор копирования для Square\n";
}

Square::Square(Square&& other) noexcept : center_(std::move(other.center_)), side_length_(other.side_length_) {
  std::cout << "Вызван конструктор перемещения для Square\n";
}

std::string Square::Description() const {
  std::cout << "Вызван метод Description для Square\n";
  return std::format("Это {}, {}", Shape::Description(), ToString());
}

std::string Square::ToString() const {
  std::cout << "Вызван метод ToString для Square\n";
  return std::format("Square({}, {})", center_.ToString(), side_length_);
}

double Square::Area() const {
  std::cout << "Вызван метод Area для Square\n";
  return side_length_ * side_length_;
}

double Square::Perimeter() const {
  std::cout << "Вызван метод Perimeter для Square\n";
  return 4 * side_length_;
}