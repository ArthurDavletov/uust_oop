#pragma once
#include <string>

class Shape {
public:
  Shape();
  virtual std::string ToString() const = 0;
  virtual ~Shape();
};