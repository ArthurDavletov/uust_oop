#include "shape.h"
#include <iostream>
#include <string>

Shape::Shape() {
  std::cout << "Вызван конструктор по умолчанию для Shape\n";
}

std::string Shape::Description() const {
  return "Это Shape";
}

Shape::~Shape() {
  std::cout << "Вызван деструктор для Shape\n";
}