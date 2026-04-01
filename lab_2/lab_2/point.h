#pragma once
#include <string>

class Point {
public:
  Point();
  Point(double x, double y);
  double GetX() const { return x_; }
  double GetY() const { return y_; }
  std::string ToString() const;
  ~Point();

private:
  double x_ = 0;
  double y_ = 0;
};
