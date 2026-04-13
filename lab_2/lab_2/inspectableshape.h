#pragma once
#include <string>
#include "shape.h"

class InspectableShape : public Shape {
public:
  std::string Description() const;
  std::string ToString() const override;
  std::string RevealProtectedInfo() const;
};
