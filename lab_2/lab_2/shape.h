#pragma once
#include <string>

class Shape {
public:
  virtual std::string ToString() const = 0;
  virtual ~Shape() = default;
};