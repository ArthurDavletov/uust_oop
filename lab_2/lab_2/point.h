#pragma once
#include <string>

class Point {
public:
  Point();
  Point(double x, double y);
  Point(const Point& other);
  Point(Point&& other) noexcept;
  std::string Description() const;
  double GetX() const { return x_; }
  double GetY() const { return y_; }
  void SetX(double x);
  void SetY(double y);
  void SetXY(double x, double y);
  std::string ToString() const;
  ~Point();

private:
  double x_ = 0;
  double y_ = 0;
};
