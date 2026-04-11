#include <iostream>
#include <windows.h>
#include <format>

#include "point.h"
#include "shape.h"
#include "segment.h"
#include "segmentptr.h"

void PrintTitle(const std::string& title) {
  char border[] = "======";
  std::cout << std::format("\n{0} {1} {0}\n", border, title);
}

void StaticObjectsDemo() {
  PrintTitle("StaticObjectsDemo");
  Point p1;
  Point p2(1, 2);
  Point p3 = p2;

  std::cout << p1.ToString() << "\n";
  std::cout << p2.ToString() << "\n";
  std::cout << p3.ToString() << "\n";
}

void DynamicObjectsDemo() {
  PrintTitle("DynamicObjectsDemo");
  Point* p = new Point(3, 4);
  std::cout << p->ToString() << "\n";
  delete p;
}

void ObjectCopyDemo() {
  PrintTitle("ObjectCopyDemo");
  Point a(1, 2);
  Point b = a;  // копия объекта
  b.SetX(100);
  std::string a_info = a.ToString();
  std::string b_info = b.ToString();
  std::cout << std::format("a = {}\nb = {}\n", a_info, b_info);
}

void PointerCopyDemo() {
  PrintTitle("PointerCopyDemo");
  Point* a = new Point(1, 2);
  Point* b = a;  // копия указателя

  b->SetX(200);
  std::string a_info = a->ToString();
  std::string b_info = b->ToString();
  std::cout << std::format("a = {}\nb = {}\n", a_info, b_info);
  delete a;
  b = nullptr;
}

void BasePointerDemo() {
  PrintTitle("BasePointerDemo");
  Shape* s = new Segment(0, 0, 3, 4);

  std::string s_description = s->Description();
  std::string s_info = s->ToString();
  std::cout << s_description << "\n";  // Shape::Description()
  std::cout << s_info << "\n";         // Segment::ToString()

  delete s;
}

void CompositionDemo() {
  PrintTitle("CompositionDemo");
  Segment seg(Point(0, 0), Point(1, 1));
  std::string seg_description = seg.Description();
  std::cout << seg_description << "\n";

  SegmentPtr segPtr(Point(2, 2), Point(3, 3));
  std::string segPtr_description = segPtr.Description();
  std::cout << segPtr_description << "\n";
}

int main() {
  // Исправление русского языка в консоли Windows
  SetConsoleCP(CP_UTF8);
  SetConsoleOutputCP(CP_UTF8);
  StaticObjectsDemo();
  DynamicObjectsDemo();
  ObjectCopyDemo();
  PointerCopyDemo();
  BasePointerDemo();
  CompositionDemo();
  return 0;
}