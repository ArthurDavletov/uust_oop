#include <string>
#include <iostream>
#include <cmath>
#include <utility>
#include <format>
#include "segment.h"
#include "point.h"

Segment::Segment() {
  std::cout << "Вызван конструктор по умолчанию для Segment\n";
}

Segment::~Segment() {
  std::cout << "Вызван деструктор для Segment\n";
}

Segment::Segment(double x1, double y1, double x2, double y2)
    : p1_(Point(x1, y1)), p2_(Point(x2, y2)) {
  std::cout << "Вызван конструктор с параметрами (4 числа) для Segment\n";
}

Segment::Segment(const Point& p1, const Point& p2) : p1_(p1), p2_(p2) {
  std::cout << "Вызван конструктор с параметрами (2 точки) для Segment\n";
}

Segment::Segment(const Segment& other) : p1_(other.p1_), p2_(other.p2_) {
  std::cout << "Вызван конструктор копирования для Segment\n";
}

Segment::Segment(Segment&& other) noexcept : p1_(std::move(other.p1_)), p2_(std::move(other.p2_)) {
  std::cout << "Вызван конструктор перемещения для Segment\n";
}

double Segment::GetLength() const {
  std::cout << "Вызван метод GetLength для Segment\n";
  double dx = p2_.GetX() - p1_.GetX();
  double dy = p2_.GetY() - p1_.GetY();
  return std::sqrt(dx * dx + dy * dy);
}

std::string Segment::ToString() const {
  std::cout << "Вызван метод ToString для Segment\n";
  return std::format("Segment({}, {})", p1_.ToString(), p2_.ToString());
}