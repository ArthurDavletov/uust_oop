#pragma once
#include <string>
#include "shape.h"
#include "point.h"

class SegmentPtr : Shape {
public:
  SegmentPtr();
  SegmentPtr(const Point& start, const Point& end);
  std::string Description() const;
  std::string ToString() const override;
  ~SegmentPtr() override;
private:
  Point* start_ = nullptr;
  Point* end_ = nullptr;
};