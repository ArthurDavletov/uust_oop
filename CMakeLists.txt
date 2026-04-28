cmake_minimum_required(VERSION 3.20)

project(uust_oop)

set(CMAKE_CXX_STANDARD 20) # std::format добавлен в C++20
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(lab2
  lab_2/lab_2/main.cpp
  lab_2/lab_2/circle.cpp
  lab_2/lab_2/closedshape.cpp
  lab_2/lab_2/coloredpoint.cpp
  lab_2/lab_2/inspectableshape.cpp
  lab_2/lab_2/point.cpp
  lab_2/lab_2/segment.cpp
  lab_2/lab_2/segmentptr.cpp
  lab_2/lab_2/shape.cpp
  lab_2/lab_2/square.cpp
)
add_executable(lab5 lab_5/lab_5/main.cpp)