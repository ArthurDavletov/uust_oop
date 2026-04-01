#ifndef GEOMETRY_H
#define GEOMETRY_H

#include <cstdint>

class Point {
public:
 Point(int64_t x, int64_t y): x_(x), y_(y) {}

private:
  int64_t x_ = 0;
  int64_t y_ = 0;
};


#endif  // !GEOMETRY_H
