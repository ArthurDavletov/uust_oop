#include "inspectableshape.h"
#include <format>
#include <iostream>
#include <string>

std::string InspectableShape::Description() const {
  std::cout << "[DEBUG] Вызван метод Description для InspectableShape\n";
  return std::format("Это InspectableShape, {}", BaseInfo());
}

std::string InspectableShape::ToString() const {
  std::cout << "[DEBUG] Вызван метод ToString для InspectableShape\n";
  return "InspectableShape()";
}

std::string InspectableShape::RevealProtectedInfo() const {
  std::cout << "[DEBUG] Вызван метод RevealProtectedInfo для InspectableShape\n";
  return BaseInfo();
}
