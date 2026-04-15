#pragma once
#include <string>
#include "shape.h"
#include "point.h"

class Segment : public Shape {
public:
  Segment();
  ~Segment() override;
  Segment(double x1, double y1, double x2, double y2);
  Segment(const Point& p1, const Point& p2);
  Segment(const Segment& other);
  Segment(Segment&& other) noexcept;
  std::string Description() const;
  double GetLength() const;
  std::string ToString() const override;
private:
  Point p1_;
  Point p2_;
};