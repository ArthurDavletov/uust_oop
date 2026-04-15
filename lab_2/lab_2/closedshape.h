#pragma once
#include "shape.h"
#include <string>

class ClosedShape : public Shape {
public:
  ClosedShape();
  std::string Description() const;
  virtual double Area() const = 0;
  virtual double Perimeter() const = 0;
  std::string ToString() const override = 0;
  virtual ~ClosedShape() override;
};