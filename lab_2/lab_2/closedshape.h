#pragma once
#include "shape.h"

class ClosedShape : public Shape {
public:
  virtual double Area() const = 0;
  virtual double Perimeter() const = 0;
};