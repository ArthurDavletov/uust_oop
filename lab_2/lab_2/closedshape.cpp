#include "closedshape.h"
#include <iostream>

ClosedShape::ClosedShape() {
  std::cout << "Вызван конструктор по умолчанию для ClosedShape\n";
}

ClosedShape::~ClosedShape() {
  std::cout << "Вызван деструктор для ClosedShape\n";
}