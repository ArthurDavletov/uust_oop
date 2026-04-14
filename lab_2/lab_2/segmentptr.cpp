#include "segmentptr.h"
#include <iostream>
#include <string>
#include <format>
#include "point.h"

SegmentPtr::SegmentPtr() : start_(new Point()), end_(new Point()) {
  std::cout << "[DEBUG] Вызван конструктор по умолчанию для SegmentPtr\n";
}

SegmentPtr::SegmentPtr(const Point& start, const Point& end)
    : start_(new Point(start)), end_(new Point(end)) {
  std::cout << "[DEBUG] Вызван конструктор с параметрами для SegmentPtr\n";
}

SegmentPtr::SegmentPtr(const SegmentPtr& other) {
  std::cout << "[DEBUG] Вызван конструктор копирования для SegmentPtr\n";
  start_ = end_ = nullptr;
  if (other.start_) {
    start_ = new Point(*other.start_);
  }
  if (other.end_) {
    end_ = new Point(*other.end_);
  }
}
  SegmentPtr::SegmentPtr(SegmentPtr&& other) noexcept
    : start_(other.start_), end_(other.end_) {
  std::cout << "[DEBUG] Вызван конструктор перемещения для SegmentPtr\n";
  other.start_ = nullptr;
  other.end_ = nullptr;
}

SegmentPtr::~SegmentPtr() {
  std::cout << "[DEBUG] Вызван деструктор для SegmentPtr\n";
  delete start_;
  delete end_;
}

std::string SegmentPtr::Description() const {
  std::cout << "[DEBUG] Вызван метод Description для SegmentPtr\n";
  return std::format("Это SegmentPtr с координатами начала ({}, {}) и конца ({}, {})", start_->GetX(), start_->GetY(), end_->GetX(), end_->GetY());
}

std::string SegmentPtr::ToString() const {
  std::cout << "[DEBUG] Вызван метод ToString для SegmentPtr\n";
  return std::format("SegmentPtr(start = {}, end = {})", start_->ToString(), end_->ToString());
}

void SegmentPtr::SetStart(double x, double y) {
  std::cout << "[DEBUG] Вызван метод SetStart для SegmentPtr\n";
  start_->SetXY(x, y);
}

void SegmentPtr::SetEnd(double x, double y) {
  std::cout << "[DEBUG] Вызван метод SetEnd для SegmentPtr\n";
  end_->SetXY(x, y);
}
