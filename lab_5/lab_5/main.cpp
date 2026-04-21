#include <iostream>
#include <memory>
#include <string>
#include <string_view>
#include <utility>
#include <vector>
#include <windows.h>

void PrintTitle(const std::string_view title) {
  std::cout << "\n========== " << title << " ==========\n";
}

void PrintCase(const std::string_view title) {
  std::cout << "\n-- " << title << " --\n";
}

const char* BoolText(const bool value) {
  if (value) {
    return "true";
  }
  return "false";
}




class Shape {
public:
  Shape() {
    std::cout << "[DEBUG] Конструктор по-умолчанию Shape\n";
  }

  Shape(const Shape&) {
    std::cout << "[DEBUG] Конструктор копирования Shape\n";
  }

  virtual ~Shape() {
    std::cout << "[DEBUG] Деструктор Shape\n";
  }

  virtual std::string classname() const {
    return "Shape";
  }

  virtual bool isA(const std::string& name) const {
    return name == "Shape";
  }

  void method1CallsMethod2NonVirtual() const {
    std::cout << "[DEBUG] Shape::method1CallsMethod2NonVirtual -> ";
    method2NonVirtual();
  }

  void method1CallsMethod2Virtual() const {
    std::cout << "[DEBUG] Shape::method1CallsMethod2Virtual -> ";
    method2Virtual();
  }

  void info() const {
    std::cout << "[DEBUG] Shape::info (невиртуальный метод базового класса)\n";
  }

  void method2NonVirtual() const {
    std::cout << "[DEBUG] Shape::method2NonVirtual\n";
  }

  virtual void method2Virtual() const {
    std::cout << "[DEBUG] Shape::method2Virtual\n";
  }

  virtual void draw() const {
    std::cout << "[DEBUG] Shape::draw (базовая реализация виртуального метода)\n";
  }

  virtual std::unique_ptr<Shape> clone() const = 0;
};





class ClosedShape : public Shape {
public:
  ClosedShape() {
    std::cout << "[DEBUG] Конструктор по-умолчанию ClosedShape\n";
  }

  ClosedShape(const ClosedShape& other) : Shape(other) {
    std::cout << "[DEBUG] Конструктор копирования ClosedShape\n";
  }

  ~ClosedShape() override {
    std::cout << "[DEBUG] Деструктор ClosedShape\n";
  }

  std::string classname() const override {
    return "ClosedShape";
  }

  bool isA(const std::string& name) const override {
    return name == "ClosedShape" || Shape::isA(name);
  }
};





class Circle : public ClosedShape {
public:
  explicit Circle(const double radius = 1.0) : radius_(radius) {
    std::cout << "[DEBUG] Конструктор по-умолчанию Circle, radius = " << radius_ << '\n';
  }

  Circle(const Circle& other) : ClosedShape(other), radius_(other.radius_) {
    std::cout << "[DEBUG] Конструктор копирования Circle, radius = " << radius_ << '\n';
  }

  ~Circle() override {
    std::cout << "[DEBUG] Деструктор Circle, radius = " << radius_ << '\n';
  }

  std::string classname() const override {
    return "Circle";
  }

  bool isA(const std::string& name) const override {
    return name == "Circle" || ClosedShape::isA(name);
  }

  void info() const {
    std::cout << "[DEBUG] Circle::info (невиртуальный метод потомка)\n";
  }

  void method2NonVirtual() const {
    std::cout << "[DEBUG] Circle::method2NonVirtual (сокрытие, а не виртуальность)\n";
  }

  void method2Virtual() const override {
    std::cout << "[DEBUG] Circle::method2Virtual\n";
  }

  void draw() const override {
    std::cout << "[DEBUG] Circle::draw (переопределенный виртуальный метод)\n";
  }

  std::unique_ptr<Shape> clone() const override {
    return std::make_unique<Circle>(*this);
  }

  void circleOnly() const {
    std::cout << "[DEBUG] Circle::circleOnly, radius = " << radius_ << '\n';
  }

private:
  double radius_ = 0.0;
};



class Square : public ClosedShape {
public:
  explicit Square(const double side = 1.0) : side_(side) {
    std::cout << "[DEBUG] Конструктор по-умолчанию Square, side = " << side_ << '\n';
  }

  Square(const Square& other) : ClosedShape(other), side_(other.side_) {
    std::cout << "[DEBUG] Конструктор копирования Square, side = " << side_ << '\n';
  }

  ~Square() override {
    std::cout << "[DEBUG] Деструктор Square, side = " << side_ << '\n';
  }

  std::string classname() const override {
    return "Square";
  }

  bool isA(const std::string& name) const override {
    return name == "Square" || ClosedShape::isA(name);
  }

  void info() const {
    std::cout << "[DEBUG] Square::info (одноименный, но невиртуальный метод потомка)\n";
  }

  std::unique_ptr<Shape> clone() const override {
    return std::make_unique<Square>(*this);
  }

  void squareOnly() const {
    std::cout << "[DEBUG] Square::squareOnly, side = " << side_ << '\n';
  }

private:
  double side_ = 0.0;
};



class Segment : public Shape {
public:
  explicit Segment(const double length = 1.0) : length_(length) {
    std::cout << "[DEBUG] Конструктор по-умолчанию Segment, length = " << length_ << '\n';
  }

  Segment(const Segment& other) : Shape(other), length_(other.length_) {
    std::cout << "[DEBUG] Конструктор копирования Segment, length = " << length_ << '\n';
  }

  ~Segment() override {
    std::cout << "[DEBUG] Деструктор Segment, length = " << length_ << '\n';
  }

  std::string classname() const override {
    return "Segment";
  }

  bool isA(const std::string& name) const override {
    return name == "Segment" || Shape::isA(name);
  }

  void draw() const override {
    std::cout << "[DEBUG] Segment::draw\n";
  }

  std::unique_ptr<Shape> clone() const override {
    return std::make_unique<Segment>(*this);
  }

  void segmentOnly() const {
    std::cout << "[DEBUG] Segment::segmentOnly, length = " << length_ << '\n';
  }

private:
  double length_ = 0.0;
};








class Base {
public:
  Base() : id_(NextId()) {
    std::cout << "[DEBUG] Base() -> #" << id_ << '\n';
  }

  Base(Base* obj) : id_(NextId()) {
    std::cout << "[DEBUG] Base(Base*) -> #" << id_
              << ", source = #" << obj->Id() << '\n';
  }

  Base(Base& obj) : id_(NextId()) {
    std::cout << "[DEBUG] Base(Base&) -> #" << id_ << ", source = #" << obj.Id() << '\n';
  }

  virtual ~Base() {
    std::cout << "[DEBUG] ~Base() -> #" << id_ << '\n';
  }

  int Id() const {
    return id_;
  }

  virtual std::string RuntimeType() const {
    return "Base";
  }

private:
  static int NextId() {
    static int next_id = 1;
    return next_id++;
  }

  int id_ = 0;
};




class Desc : public Base {
public:
  Desc() : Base() {
    std::cout << "[DEBUG] Desc() for object #" << Id() << '\n';
  }

  Desc(Desc* obj) : Base(obj) {
    std::cout << "[DEBUG] Desc(Desc*) for object #" << Id()
              << ", source = #" << obj->Id() << '\n';
  }

  Desc(Desc& obj) : Base(obj) {
    std::cout << "[DEBUG] Desc(Desc&) for object #" << Id() << ", source = #" << obj.Id() << '\n';
  }

  ~Desc() override {
    std::cout << "[DEBUG] ~Desc() for object #" << Id() << '\n';
  }

  std::string RuntimeType() const override {
    return "Desc";
  }

  void DescOnly() const {
    std::cout << "[DEBUG] Desc::DescOnly() for object #" << Id() << '\n';
  }
};

class TrackedResource {
public:
  explicit TrackedResource(std::string name) : name_(std::move(name)) {
    std::cout << "[DEBUG] TrackedResource(\"" << name_ << "\")\n";
  }

  ~TrackedResource() {
    std::cout << "[DEBUG] TrackedResource(\"" << name_ << "\")\n";
  }

  void Use() const {
    std::cout << "TrackedResource \"" << name_ << "\" is alive\n";
  }

private:
  std::string name_;
};








void VirtualityDemo() {
  PrintTitle("Перекрываемые и виртуальные методы");

  Circle circle(10.0);
  Square square(4.0);

  Shape* circle_as_shape = &circle;
  Circle* circle_as_circle = &circle;
  Shape* square_as_shape = &square;

  PrintCase("Невиртуальный метод с одинаковым именем");
  circle_as_shape->info();
  circle_as_circle->info();
  // Через Shape* вызывается Shape::info, потому что метод не virtual.

  PrintCase("Виртуальный метод с одинаковым именем");
  circle_as_shape->draw();
  circle_as_circle->draw();
  // Через Shape* все равно вызывается Circle::draw благодаря virtual.

  PrintCase("Базовый method1 вызывает невиртуальный method2");
  circle.method1CallsMethod2NonVirtual();
  // Вызван Shape::method2NonVirtual, потому что внутри базового метода работает статическое связывание.

  PrintCase("Базовый method1 вызывает виртуальный method2");
  circle.method1CallsMethod2Virtual();
  // Вызван Circle::method2Virtual, потому что virtual использует динамическое связывание.

  PrintCase("Когда вызывается наследуемый виртуальный метод, а когда переопределенный");
  square_as_shape->draw();
  circle_as_shape->draw();
  // Square не переопределяет draw(), поэтому получает базовую реализацию Shape::draw.
  // Circle переопределяет draw(), поэтому вызывается Circle::draw.

  PrintCase("Виртуальный деструктор");
  std::unique_ptr<Shape> cloned = circle.clone();
  std::cout << "clone() вернул объект типа " << cloned->classname() << '\n';

  Shape* poly = new Circle(42.0);
  // Удаляем Circle через Shape*
  delete poly;
  // Благодаря virtual деструктору вызвались деструкторы потомка и базовых частей.
  // Если бы деструктор Shape не был virtual, такое удаление было бы ошибкой и привело бы к undefined behavior.
}












void TypeCheckDemo() {
  PrintTitle("classname, isA, unsafe cast, dynamic_cast");

  Circle circle(5.0);
  Square square(3.0);
  Segment segment(8.0);

  std::vector<Shape*> shapes = { &circle, &square, &segment };
  // Один vector<Shape*> может хранить объекты разных потомков: Circle, Square и Segment

  PrintCase("classname() и проблема точного совпадения");
  for (Shape* shape : shapes) {
    std::cout << shape->classname()
              << ": classname()==\"Shape\" -> " << BoolText(shape->classname() == "Shape")
              << ", isA(\"Shape\") -> " << BoolText(shape->isA("Shape")) << '\n';
  }
  // classname() возвращает только самое конкретное имя класса.
  // Поэтому Circle является Shape, но сравнение classname()=="Shape" даст false.
  // Еще одна проблема classname(): это строка, а значит легко ошибиться в названии класса.

  PrintCase("isA() понимает всю цепочку наследования");
  std::cout << "circle.isA(\"Circle\") = " << BoolText(circle.isA("Circle")) << '\n';
  std::cout << "circle.isA(\"ClosedShape\") = " << BoolText(circle.isA("ClosedShape")) << '\n';
  std::cout << "circle.isA(\"Shape\") = " << BoolText(circle.isA("Shape")) << '\n';
  std::cout << "circle.isA(\"Segment\") = " << BoolText(circle.isA("Segment")) << '\n';

  PrintCase("Опасное приведение типов");
  Shape* maybe_circle = &square;
  Circle* forced_circle = static_cast<Circle*>(maybe_circle);
  // static_cast<Circle*>(Shape* на Square) компилируется, но это плохо.

  PrintCase("Ручная безопасная проверка перед static_cast");
  if (maybe_circle->isA("Circle")) {
    Circle* safe_circle = static_cast<Circle*>(maybe_circle);
    safe_circle->circleOnly();
  } else {
    std::cout << "Объект не является Circle.\n";  // выводится это
  }

  Shape* definitely_circle = &circle;
  if (definitely_circle->isA("Circle")) {
    Circle* safe_circle = static_cast<Circle*>(definitely_circle);
    safe_circle->circleOnly();
  }

  PrintCase("Стандартное безопасное приведение через dynamic_cast");
  for (Shape* shape : shapes) {
    Circle* current_circle = dynamic_cast<Circle*>(shape);
    if (current_circle) {
      std::cout << shape->classname() << " успешно приведен к Circle*: ";
      current_circle->circleOnly();
    } else {
      std::cout << "Объект не является Circle, dynamic_cast вернул nullptr.\n ";
    }
  }
}






void func1(Base obj) {
  PrintCase("func1(Base obj)");
  std::cout << "[DEBUG] Внутри func1 создана локальная копия объекта #" << obj.Id()
            << ", runtime type = " << obj.RuntimeType() << '\n';

  if (Desc* desc = dynamic_cast<Desc*>(&obj)) {
    desc->DescOnly();
  } else {
    std::cout << "dynamic_cast к Desc* не сработал: при передаче по значению возможен slicing.\n";
  }
}

void func2(Base* obj) {
  PrintCase("func2(Base* obj)");
  std::cout << "[DEBUG] Передан указатель на объект #" << obj->Id()
            << ", runtime type = " << obj->RuntimeType() << '\n';

  if (Desc* desc = dynamic_cast<Desc*>(obj)) {
    desc->DescOnly();
  } else {
    std::cout << "Это действительно Base, а не Desc.\n";
  }
}

void func3(Base& obj) {
  PrintCase("func3(Base& obj)");
  std::cout << "[DEBUG] Передана ссылка на объект #" << obj.Id()
            << ", runtime type = " << obj.RuntimeType() << '\n';

  if (Desc* desc = dynamic_cast<Desc*>(&obj)) {
    desc->DescOnly();
  } else {
    std::cout << "Это действительно Base, а не Desc.\n";
  }
}



void ParameterPassingDemo() {
  PrintTitle("Передача объектов в функции");

  Base base;
  Base base_from_ptr(&base);
  Base base_from_ref(base);

  Desc desc;
  Desc desc_from_ptr(&desc);
  Desc desc_from_ref(desc);

  std::cout << "Специально созданы объекты через Base(Base*), Base(Base&), Desc(Desc*), Desc(Desc&).\n";
  std::cout << "ID созданных объектов: "
            << base.Id() << ", "
            << base_from_ptr.Id() << ", "
            << base_from_ref.Id() << ", "
            << desc.Id() << ", "
            << desc_from_ptr.Id() << ", "
            << desc_from_ref.Id() << '\n';

  PrintCase("Передаем Base");
  func1(base);
  func2(&base);
  func3(base);

  PrintCase("Передаем Desc");
  func1(desc);
  func2(&desc);
  func3(desc);

  std::cout << "\nИтог:\n";
  std::cout << "func1(Base obj) копирует объект и может срезать Desc до Base.\n";
  std::cout << "func2(Base* obj) не копирует объект, но требует проверять nullptr и помнить про владение.\n";
  std::cout << "func3(Base& obj) не копирует объект и не может быть nullptr, но ссылка обязана ссылаться на существующий объект.\n";
}


// func1/func2/func3 работают со static-объектами.
Base func1() {
  PrintCase("func1()");
  static Base obj;
  std::cout << "Возвращаем копию static Base #" << obj.Id() << '\n';
  return obj;
}

Base* func2() {
  PrintCase("func2()");
  static Base obj;
  std::cout << "Возвращаем указатель на static Base #" << obj.Id() << '\n';
  return &obj;
}

Base& func3() {
  PrintCase("func3()");
  static Base obj;
  std::cout << "Возвращаем ссылку на static Base #" << obj.Id() << '\n';
  return obj;
}

Base func4() {
  PrintCase("func4()");
  Base* obj = new Base();
  std::cout << "Создан dynamic Base #" << obj->Id() << ".\n";

  // Ниже оставлен закомментированный вариант, в котором возникала утечка памяти:
  // return *obj;
  // После такого return указатель obj теряется, а delete вызвать уже некому.

  Base copy = *obj;
  std::cout << "Копируем dynamic-объект в новый Base #" << copy.Id()
            << " и сразу удаляем исходный объект.\n";
  delete obj;
  return copy;
}

Base* func5() {
  PrintCase("func5()");
  Base* obj = new Base();
  std::cout << "Создан dynamic Base #" << obj->Id()
            << ", возвращаем Base*. Вызывать delete обязаны снаружи функции.\n";
  return obj;
}

Base& func6() {
  PrintCase("func6()");
  Base* obj = new Base();
  std::cout << "Создан dynamic Base #" << obj->Id()
            << ", возвращаем Base&. Удалять объект все равно придется вручную.\n";
  return *obj;
}









void ReturnDemo() {
  PrintTitle("Возврат объектов из функций");

  Base value_from_static = func1();
  std::cout << "В локальную переменную получена копия #" << value_from_static.Id() << '\n';

  Base* ptr_from_static = func2();
  std::cout << "Получен указатель на static объект #" << ptr_from_static->Id() << '\n';

  Base& ref_from_static = func3();
  std::cout << "Получена ссылка на static объект #" << ref_from_static.Id() << '\n';

  Base value_from_dynamic = func4();
  std::cout << "В локальную переменную получена копия #" << value_from_dynamic.Id()
            << ", а исходный dynamic-объект из func4 уже удален внутри самой функции.\n";

  Base* ptr_from_dynamic = func5();
  std::cout << "Получен Base* на dynamic объект #" << ptr_from_dynamic->Id() << '\n';

  Base& ref_from_dynamic = func6();
  std::cout << "Получен Base& на dynamic объект #" << ref_from_dynamic.Id() << '\n';

  std::cout << "\nОсвобождаем только то, чем реально владеем:\n";
  delete ptr_from_dynamic;  // Если удалить эту строку, объект из func5() утечет.
  delete &ref_from_dynamic; // Если удалить эту строку, объект из func6() утечет.

  // static-объекты из func2/func3 удалять нельзя: они живут до завершения программы.\n"
  // func4 теперь тоже без утечки: внутри функции исходный dynamic-объект удаляется вручную.\n";
}









void TakeUnique(std::unique_ptr<TrackedResource> resource) {
  PrintCase("TakeUnique(unique_ptr)");
  resource->Use();
  std::cout << "В конце функции unique_ptr уничтожится и удалит объект, если владение больше никуда не передавалось.\n";
}

std::unique_ptr<TrackedResource> MakeUniqueResource(const std::string& name) {
  PrintCase("MakeUniqueResource()");
  auto resource = std::make_unique<TrackedResource>(name);
  std::cout << "Возвращаем unique_ptr из фабричной функции.\n";
  return resource;
}

void ObserveShared(const std::shared_ptr<TrackedResource>& resource) {
  PrintCase("ObserveShared(shared_ptr)");
  std::cout << "use_count = " << resource.use_count() << '\n';
  resource->Use();
}

std::shared_ptr<TrackedResource> CopyShared(std::shared_ptr<TrackedResource> resource) {
  PrintCase("CopyShared(shared_ptr)");
  std::cout << "После передачи по значению use_count = " << resource.use_count() << '\n';
  return resource;
}




void SmartPointersDemo() {
  PrintTitle("Умные указатели");

  PrintCase("Обычный локальный объект");
  {
    TrackedResource local("stack object");
    local.Use();
    std::cout << "Локальный объект уничтожится строго в конце блока.\n";
  }

  PrintCase("unique_ptr и перенос времени жизни");
  std::unique_ptr<TrackedResource> outer_unique;
  {
    auto inner_unique = std::make_unique<TrackedResource>("unique moved out of inner scope");
    inner_unique->Use();
    outer_unique = std::move(inner_unique);
    std::cout << "inner_unique после move == nullptr -> " << BoolText(inner_unique == nullptr) << '\n';
  }
  // Внутренний блок уже закончился, но объект все еще жив, потому что владелец теперь outer_unique.
  outer_unique->Use();
  TakeUnique(std::move(outer_unique));
  std::cout << "outer_unique после передачи владения == nullptr -> " << BoolText(outer_unique == nullptr) << '\n';

  auto produced_unique = MakeUniqueResource("unique from factory");
  produced_unique->Use();

  PrintCase("shared_ptr и совместное владение");
  auto shared = std::make_shared<TrackedResource>("shared object");
  std::cout << "После make_shared use_count = " << shared.use_count() << '\n';

  auto shared2 = shared;
  std::cout << "После копирования в shared2 use_count = " << shared.use_count() << '\n';

  ObserveShared(shared);
  auto shared3 = CopyShared(shared);
  std::cout << "После возврата shared3 use_count = " << shared.use_count() << '\n';

  shared2.reset();
  std::cout << "После shared2.reset() use_count = " << shared.use_count() << '\n';

  shared3.reset();
  std::cout << "После shared3.reset() use_count = " << shared.use_count() << '\n';

  std::cout << "Когда исчезнет последний shared_ptr, объект будет удален автоматически.\n";
}




int main() {
  SetConsoleCP(CP_UTF8);
  SetConsoleOutputCP(CP_UTF8);

  VirtualityDemo();
  TypeCheckDemo();
  ParameterPassingDemo();
  ReturnDemo();
  SmartPointersDemo();

  PrintTitle("Конец программы");
  return 0;
}
