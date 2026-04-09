#include "shape.h"
#include <iostream>

Shape::Shape() {
  std::cout << "Вызван конструктор по умолчанию для Shape\n";
}

Shape::~Shape() {
  std::cout << "Вызван деструктор для Shape\n";
}