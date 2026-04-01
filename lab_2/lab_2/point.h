#pragma once
#include <cstdint>
#include <string>

class Point {
public:
  Point();
  Point(int64_t x, int64_t y);
  int64_t GetX() const { return x_; }
  int64_t GetY() const { return y_; }
  std::string ToString() const;
  ~Point();

private:
  int64_t x_ = 0;
  int64_t y_ = 0;
};
