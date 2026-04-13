#include "closedshape.h"
#include <iostream>
#include <string>

ClosedShape::ClosedShape() {
  std::cout << "[DEBUG] Вызван конструктор по умолчанию для ClosedShape\n";
}

std::string ClosedShape::Description() const {
  std::cout << "[DEBUG] Вызван метод Description для ClosedShape\n";
  return "Это ClosedShape";
}

ClosedShape::~ClosedShape() {
  std::cout << "[DEBUG] Вызван деструктор для ClosedShape\n";
}