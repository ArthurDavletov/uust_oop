#include "segmentptr.h"
#include <iostream>
#include <string>
#include <format>

SegmentPtr::SegmentPtr() {
  std::cout << "Вызван конструктор по умолчанию для SegmentPtr\n";
}

SegmentPtr::SegmentPtr(const Point& start, const Point& end) {
  std::cout << "Вызван конструктор с параметрами для SegmentPtr\n";
  start_ = new Point(start);
  end_ = new Point(end);
}

SegmentPtr::~SegmentPtr() {
  std::cout << "Вызван деструктор для SegmentPtr\n";
  delete start_;
  delete end_;
}

std::string SegmentPtr::Description() const {
  return std::format("Это SegmentPtr с координатами начала ({}, {}) и конца ({}, {})", start_->GetX(), start_->GetY(), end_->GetX(), end_->GetY());
}

std::string SegmentPtr::ToString() const {
  return std::format("SegmentPtr(start = {}, end = {})", start_->ToString(), end_->ToString());
}
