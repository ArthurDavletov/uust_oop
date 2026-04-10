#pragma once
#include <string>

class Shape {
public:
  Shape();
  std::string Description() const;
  virtual std::string ToString() const = 0;
  virtual ~Shape();
};