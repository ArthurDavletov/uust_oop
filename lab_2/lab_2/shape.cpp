#include "shape.h"
#include <iostream>
#include <string>

Shape::Shape() {
  std::cout << "Вызван конструктор по умолчанию для Shape\n";
}

std::string Shape::Description() const {
  std::cout << "Вызван метод Description для Shape\n";
  return "Это Shape";
}

std::string Shape::BaseInfo() const {
  std::cout << "Вызван метод BaseInfo для Shape\n";
  return "Базовая информация о фигуре, вызванная из protected-функции";
}

Shape::~Shape() {
  std::cout << "Вызван деструктор для Shape\n";
}