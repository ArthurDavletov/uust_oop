#include <iostream>
#include <format>
#include <string>

#ifdef _WIN32
#include <windows.h>
#endif

#include "point.h"
#include "shape.h"
#include "inspectableshape.h"
#include "segment.h"
#include "segmentptr.h"
#include "circle.h"
#include "square.h"
#include "coloredpoint.h"

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
  Point* p1 = new Point();
  Point* p2 = new Point(3, 4);
  Point* p3 = new Point(*p2);

  std::cout << p1->ToString() << "\n";
  std::cout << p2->ToString() << "\n";
  std::cout << p3->ToString() << "\n";

  delete p1;
  delete p2;
  delete p3;
}

void PointerAssignmentDemo() {
  PrintTitle("PointerAssignmentDemo");
  Point* original = new Point(1, 2);
  Point* alias = nullptr;

  alias = original;
  alias->SetX(200);

  std::cout << std::format("original = {}\nalias = {}\n",
                           original->ToString(), alias->ToString());

  delete original;
  original = alias = nullptr;
}

void CompositionDemo() {
  PrintTitle("CompositionDemo");
  Segment segment_default;
  Segment segment_param(Point(0, 0), Point(1, 1));
  Segment segment_copy(segment_param);

  SegmentPtr ptr_default;
  SegmentPtr ptr_param(Point(2, 2), Point(3, 3));
  SegmentPtr ptr_copy(ptr_param);

  ptr_copy.SetStart(20, 20);
  ptr_copy.SetEnd(30, 30);
  ptr_default.SetStart(-2, -2);
  ptr_default.SetEnd(-3, -3);

  std::cout << segment_default.ToString() << "\n";
  std::cout << segment_param.Description() << "\n";
  std::cout << segment_copy.ToString() << "\n";
  std::cout << ptr_default.ToString() << "\n";
  std::cout << ptr_param.Description() << "\n";
  std::cout << ptr_copy.ToString() << "\n";
}

void AccessModifiersDemo() {
  PrintTitle("AccessModifiersDemo");
  Point point(7, 8);
  InspectableShape shape;

  std::cout << point.ToString() << "\n";
  std::cout << shape.RevealProtectedInfo() << "\n";

  // public: программа может вызывать Point::SetXY и Point::ToString
  point.SetXY(9, 10);
  std::cout << point.ToString() << "\n";
  // protected: программа не может вызвать Shape::BaseInfo напрямую, но класс может
  // private: программа не может обратиться к Point::x_ и Point::y_ напрямую

  // point.x_ = 10; - ошибка
  // shape.BaseInfo(); - ошибка
}

void InheritanceWithoutOwnCtorDemo() {
  PrintTitle("InheritanceWithoutOwnCtorDemo");
  InspectableShape shape;
  std::cout << shape.Description() << "\n";
  std::cout << shape.ToString() << "\n";
}

void DerivedConstructorsDemo() {
  PrintTitle("DerivedConstructorsDemo");
  Square square_default;
  Square square_param(Point(0, 0), 5);
  Square square_copy(square_param);

  Circle circle_default;
  Circle circle_param(Point(1, 1), 3);
  Circle circle_copy(circle_param);

  std::cout << square_default.ToString() << "\n";
  std::cout << square_param.Description() << "\n";
  std::cout << square_copy.ToString() << "\n";
  std::cout << circle_default.ToString() << "\n";
  std::cout << circle_param.Description() << "\n";
  std::cout << circle_copy.ToString() << "\n";
}

void DerivedDynamicDestructionDemo() {
  PrintTitle("DerivedDynamicDestructionDemo");
  Shape* shape1 = new Segment(0, 0, 3, 4);
  Shape* shape2 = new Square(Point(2, 2), 6);
  Shape* shape3 = new Circle(Point(5, 5), 2);

  std::cout << shape1->Description() << "\n";
  std::cout << shape1->ToString() << "\n";
  std::cout << shape2->Description() << "\n";
  std::cout << shape2->ToString() << "\n";
  std::cout << shape3->Description() << "\n";
  std::cout << shape3->ToString() << "\n";
  // Через Shape* доступны только методы интерфейса Shape

  delete shape1;
  delete shape2;
  delete shape3;
}

void MethodHidingDemo() {
  PrintTitle("MethodHidingDemo");
  Segment segment(0, 0, 10, 0);
  Shape* base_ptr = &segment;

  std::cout << std::format("segment.Description() = {}\n", segment.Description());
  std::cout << std::format("base_ptr->Description() = {}\n", base_ptr->Description());
  std::cout << std::format("base_ptr->ToString() = {}\n", base_ptr->ToString());
  std::cout << "base_ptr->GetLength() недоступен, потому что такого метода нет в Shape\n";
}

void BasePointerAndSlicingDemo() {
  PrintTitle("BasePointerAndSlicingDemo");
  ColoredPoint colored(5, 6, "red");
  ColoredPoint derived_on_stack(7, 8, "blue");
  Point* base_ptr = &derived_on_stack;
  Point sliced = colored;

  std::cout << std::format("colored = {}\n", colored.ToString());
  std::cout << std::format("base_ptr->ToString() = {}\n", base_ptr->ToString());
  std::cout << "Через Point* можно вызывать только методы Point, которых нет в ColoredPoint-интерфейсе\n";

  sliced.SetX(500);
  colored.SetColor("green");

  std::cout << std::format("sliced = {}\n", sliced.ToString());
  std::cout << std::format("colored после редактирования = {}\n", colored.ToString());
  std::cout << "Point sliced = colored теряет поле color_ и превращает объект в Point\n";
}

int main() {
  // Исправление русского языка в консоли Windows
  #ifdef _WIN32
  SetConsoleCP(CP_UTF8);
  SetConsoleOutputCP(CP_UTF8);
  #endif

  StaticObjectsDemo();
  DynamicObjectsDemo();
  PointerAssignmentDemo();
  CompositionDemo();
  AccessModifiersDemo();
  InheritanceWithoutOwnCtorDemo();
  DerivedConstructorsDemo();
  DerivedDynamicDestructionDemo();
  MethodHidingDemo();
  BasePointerAndSlicingDemo();
  return 0;
}
