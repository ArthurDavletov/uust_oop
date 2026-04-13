#include "coloredpoint.h"
#include <format>
#include <iostream>
#include "point.h"

ColoredPoint::ColoredPoint() {
  std::cout << "Вызван конструктор по умолчанию для ColoredPoint\n";
}

ColoredPoint::ColoredPoint(double x, double y, const std::string& color)
    : Point(x, y), color_(color) {
  std::cout << "Вызван конструктор с параметрами для ColoredPoint\n";
}

ColoredPoint::ColoredPoint(const ColoredPoint& other)
    : Point(other), color_(other.color_) {
  std::cout << "Вызван конструктор копирования для ColoredPoint\n";
}

ColoredPoint::~ColoredPoint() {
  std::cout << "Вызван деструктор для ColoredPoint\n";
}

void ColoredPoint::SetColor(const std::string& color) {
  std::cout << "Вызван метод SetColor для ColoredPoint\n";
  color_ = color;
}

std::string ColoredPoint::GetColor() const {
  std::cout << "Вызван метод GetColor для ColoredPoint\n";
  return color_;
}

std::string ColoredPoint::ToString() const {
  std::cout << "Вызван метод ToString для ColoredPoint\n";
  return std::format("ColoredPoint({}, color = {})", Point::ToString(), color_);
}
