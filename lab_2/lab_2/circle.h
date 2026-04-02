#pragma once
#include <string>
#include "closedshape.h"
#include "point.h"

class Circle : public ClosedShape {
public:
  Circle();
  Circle(const Point& center, double radius);
  ~Circle() override;
  double Area() const override;
  double Perimeter() const override;
  std::string ToString() const override;
private:
  Point center_;
  double radius_ = 0;
};