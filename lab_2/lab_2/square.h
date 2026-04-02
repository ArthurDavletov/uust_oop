#pragma once
#include <string>
#include "point.h"
#include "closedshape.h"

class Square : public ClosedShape {
public:
  Square();
  Square(const Point& center, double side_length);
  Square(const Square& other);
  Square(Square&& other) noexcept;
  ~Square() override;
  std::string ToString() const override;
  double Area() const override;
  double Perimeter() const override;
private:
  Point center_;
  double side_length_ = 0.0;
};