from typing import Iterable

from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QColor

from shapes import Shape


class ShapeStorage:
    def __init__(self) -> None:
        self._shapes: list[Shape] = []

    def add(self, shape: Shape) -> None:
        self._shapes.append(shape)

    def clear_selection(self) -> None:
        for shape in self._shapes:
            shape.set_selected(False)

    def select_all(self) -> None:
        for shape in self._shapes:
            shape.set_selected(True)

    def remove_selected(self) -> None:
        self._shapes = [shape for shape in self._shapes if not shape.is_selected()]

    def shape_at(self, point: QPointF) -> Shape | None:
        for shape in reversed(self._shapes):
            if shape.contains_point(point):
                return shape
        return None

    def selected_shapes(self) -> list[Shape]:
        return [shape for shape in self._shapes if shape.is_selected()]

    def selected_count(self) -> int:
        return len(self.selected_shapes())

    def move_selected(self, allowed_dx: float, allowed_dy: float, bounds: QRectF) -> None:
        selected = self.selected_shapes()
        if not selected:
            return

        for shape in selected:
            rect = shape.rect()
            allowed_dx = min(allowed_dx, bounds.right() - rect.right())
            allowed_dx = max(allowed_dx, bounds.left() - rect.left())
            allowed_dy = min(allowed_dy, bounds.bottom() - rect.bottom())
            allowed_dy = max(allowed_dy, bounds.top() - rect.top())

        for shape in selected:
            shape.move_by(allowed_dx, allowed_dy, bounds)

    def resize_selected(self, delta: float, bounds: QRectF) -> None:
        for shape in self.selected_shapes():
            shape.resize_by(delta, bounds)

    def recolor_selected(self, color: QColor) -> None:
        for shape in self.selected_shapes():
            shape.color = color

    def ensure_inside(self, bounds: QRectF) -> None:
        for shape in self._shapes:
            shape.ensure_inside(bounds)

    def __iter__(self) -> Iterable[Shape]:
        return iter(self._shapes)
