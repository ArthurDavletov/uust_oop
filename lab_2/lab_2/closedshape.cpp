#include "closedshape.h"
#include <iostream>
#include <string>

ClosedShape::ClosedShape() {
  std::cout << "Вызван конструктор по умолчанию для ClosedShape\n";
}

std::string ClosedShape::Description() const {
  return "Это ClosedShape";
}

ClosedShape::~ClosedShape() {
  std::cout << "Вызван деструктор для ClosedShape\n";
}