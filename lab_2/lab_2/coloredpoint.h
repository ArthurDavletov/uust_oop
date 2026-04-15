#pragma once
#include <string>
#include "point.h"

class ColoredPoint : public Point {
public:
  ColoredPoint();
  ColoredPoint(double x, double y, const std::string& color);
  ColoredPoint(const ColoredPoint& other);
  ~ColoredPoint();
  void SetColor(const std::string& color);
  std::string GetColor() const;
  std::string ToString() const;
private:
  std::string color_ = "white";
};
