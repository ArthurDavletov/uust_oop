#pragma once
#include <string>
#include "point.h"
#include "closedshape.h"

class Square : public ClosedShape {
public:
  Square();
  Square(const Point& center_, double side_length);
  ~Square() override;
  std::string ToString() const override;
  double Area() const override;
  double Perimeter() const override;
private:
  Point center_;
  double side_length_;
};