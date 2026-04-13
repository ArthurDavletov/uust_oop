#include "inspectableshape.h"
#include <format>
#include <iostream>

std::string InspectableShape::Description() const {
  std::cout << "Вызван метод Description для InspectableShape\n";
  return std::format("Это InspectableShape, {}", BaseInfo());
}

std::string InspectableShape::ToString() const {
  std::cout << "Вызван метод ToString для InspectableShape\n";
  return "InspectableShape()";
}

std::string InspectableShape::RevealProtectedInfo() const {
  std::cout << "Вызван метод RevealProtectedInfo для InspectableShape\n";
  return BaseInfo();
}
