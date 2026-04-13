#pragma once
#include <string>
#include "shape.h"
#include "point.h"

class SegmentPtr : public Shape {
public:
  SegmentPtr();
  SegmentPtr(const Point& start, const Point& end);
  SegmentPtr(const SegmentPtr& other);
  SegmentPtr(SegmentPtr&& other) noexcept;
  std::string Description() const;
  std::string ToString() const override;
  void SetStart(double x, double y);
  void SetEnd(double x, double y);
  ~SegmentPtr() override;
private:
  Point* start_ = nullptr;
  Point* end_ = nullptr;
};
