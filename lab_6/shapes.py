import math
from abc import ABC, abstractmethod
from typing import Any, Iterable

from PySide6.QtCore import QLineF, QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen, QPolygonF

__all__ = (
    "Shape",
    "RectangleShape",
    "SquareShape",
    "EllipseShape",
    "CircleShape",
    "TriangleShape",
    "RhombusShape",
    "LineShape",
    "GroupShape",
    "ShapeFactory",
)


def _rect_to_list(rect: QRectF) -> list[float]:
    return [
        round(rect.left(), 3),
        round(rect.top(), 3),
        round(rect.width(), 3),
        round(rect.height(), 3),
    ]


def _rect_from_list(values: list[int | float]) -> QRectF:
    if len(values) != 4:
        raise ValueError("Прямоугольник должен содержать 4 числа: x, y, width, height")
    return QRectF(float(values[0]), float(values[1]), float(values[2]), float(values[3]))


class Shape(ABC):
    TYPE_NAME = "shape"
    DEFAULT_WIDTH = 90.0
    DEFAULT_HEIGHT = 70.0
    MIN_SIZE = 24.0
    SELECTION_MARGIN = 4.0

    def __init__(self, rect: QRectF | None = None) -> None:
        self._rect = QRectF(rect) if rect is not None else QRectF(0, 0, self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT)
        self._color = QColor("#7070ff")
        self._selected = False

    @classmethod
    def create_at(cls, center: QPointF, bounds: QRectF) -> "Shape":
        shape = cls()
        shape.place_at(center, bounds)
        return shape

    @classmethod
    def type_name(cls) -> str:
        return cls.TYPE_NAME

    def place_at(self, center: QPointF, bounds: QRectF) -> None:
        width, height = self._normalize_size(self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT)
        rect = QRectF(center.x() - width / 2, center.y() - height / 2, width, height)
        self._rect = self._fit_into(bounds, rect)

    def draw(self, painter: QPainter) -> None:
        self._draw_shape(painter)
        if self._selected:
            painter.save()
            painter.setBrush(Qt.NoBrush)
            painter.setPen(QPen(QColor("#ff6b00"), 2, Qt.DashLine))
            painter.drawRect(self.selection_rect())
            painter.restore()

    @abstractmethod
    def _draw_shape(self, painter: QPainter) -> None:
        pass

    def contains_point(self, point: QPointF) -> bool:
        return self.selection_rect().contains(point)

    def move_by(self, dx: float, dy: float, bounds: QRectF) -> None:
        self._rect = self._fit_into(bounds, self._rect.translated(dx, dy))

    def resize_by(self, delta: float, bounds: QRectF) -> None:
        current_width = self._rect.width()
        current_height = self._rect.height()
        max_side = max(current_width, current_height)
        if max_side <= 0:
            return

        min_scale = max(self.MIN_SIZE / current_width, self.MIN_SIZE / current_height)
        scale = max((max_side + delta) / max_side, min_scale)

        width = current_width * scale
        height = current_height * scale
        width, height = self._normalize_size(width, height)

        center = self._rect.center()
        width, height = self._limit_size(width, height, center, bounds)
        rect = QRectF(center.x() - width / 2, center.y() - height / 2, width, height)
        self._rect = self._fit_into(bounds, rect)

    def scale_from(self, origin: QPointF, scale: float, bounds: QRectF) -> None:
        rect = QRectF(
            origin.x() + (self._rect.left() - origin.x()) * scale,
            origin.y() + (self._rect.top() - origin.y()) * scale,
            self._rect.width() * scale,
            self._rect.height() * scale,
        )
        width, height = self._normalize_size(max(rect.width(), self.MIN_SIZE), max(rect.height(), self.MIN_SIZE))
        rect = QRectF(rect.left(), rect.top(), width, height)
        self._rect = self._fit_into(bounds, rect)

    def ensure_inside(self, bounds: QRectF) -> None:
        self._rect = self._fit_into(bounds, self._rect)

    def rect(self) -> QRectF:
        return QRectF(self._rect)

    def selection_rect(self) -> QRectF:
        return self._rect.adjusted(
            -self.SELECTION_MARGIN,
            -self.SELECTION_MARGIN,
            self.SELECTION_MARGIN,
            self.SELECTION_MARGIN,
        )

    def set_selected(self, selected: bool) -> None:
        self._selected = selected

    def is_selected(self) -> bool:
        return self._selected

    def can_ungroup(self) -> bool:
        return False

    def take_children(self) -> list["Shape"]:
        return []

    def save(self) -> dict[str, Any]:
        return {
            "type": self.type_name(),
            "rect": _rect_to_list(self._rect),
            "color": self.color.name(),
        }

    def load(self, data: dict[str, Any], factory: "ShapeFactory") -> None:
        rect_data = data.get("rect")
        if not isinstance(rect_data, list):
            raise ValueError(f"У объекта {self.type_name()} отсутствует поле rect")

        color = QColor(str(data.get("color", "#7070ff")))
        if not color.isValid():
            raise ValueError(f"Некорректный цвет у объекта {self.type_name()}")

        self._rect = _rect_from_list(rect_data)
        self._color = color
        self._selected = False

    @property
    def color(self) -> QColor:
        return QColor(self._color)

    @color.setter
    def color(self, color: QColor) -> None:
        self._color = QColor(color)

    def _normalize_size(self, width: float, height: float) -> tuple[float, float]:
        return width, height

    def _fit_into(self, bounds: QRectF, rect: QRectF) -> QRectF:
        width = min(rect.width(), bounds.width())
        height = min(rect.height(), bounds.height())
        left = min(max(rect.left(), bounds.left()), bounds.right() - width)
        top = min(max(rect.top(), bounds.top()), bounds.bottom() - height)
        return QRectF(left, top, width, height)

    def _limit_size(self, width: float, height: float, center: QPointF, bounds: QRectF) -> tuple[float, float]:
        max_width = 2 * min(center.x() - bounds.left(), bounds.right() - center.x())
        max_height = 2 * min(center.y() - bounds.top(), bounds.bottom() - center.y())

        scale = min(1.0, max_width / width, max_height / height)
        return width * scale, height * scale


class RectangleShape(Shape):
    TYPE_NAME = "rectangle"
    DEFAULT_WIDTH = 110.0
    DEFAULT_HEIGHT = 70.0

    def _draw_shape(self, painter: QPainter) -> None:
        painter.save()
        painter.setPen(QPen(QColor("#2d3436"), 2))
        painter.setBrush(self.color)
        painter.drawRect(self._rect)
        painter.restore()

    def contains_point(self, point: QPointF) -> bool:
        return self._rect.contains(point)


class SquareShape(RectangleShape):
    TYPE_NAME = "square"
    DEFAULT_WIDTH = 80.0
    DEFAULT_HEIGHT = 80.0

    def _normalize_size(self, width: float, height: float) -> tuple[float, float]:
        size = max(width, height, self.MIN_SIZE)
        return size, size


class EllipseShape(Shape):
    TYPE_NAME = "ellipse"
    DEFAULT_WIDTH = 120.0
    DEFAULT_HEIGHT = 75.0

    def _draw_shape(self, painter: QPainter) -> None:
        painter.save()
        painter.setPen(QPen(QColor("#2d3436"), 2))
        painter.setBrush(self.color)
        painter.drawEllipse(self._rect)
        painter.restore()

    def contains_point(self, point: QPointF) -> bool:
        rect = self._rect
        rx = rect.width() / 2
        ry = rect.height() / 2
        if rx == 0 or ry == 0:
            return False
        center = rect.center()
        dx = point.x() - center.x()
        dy = point.y() - center.y()
        return (dx * dx) / (rx * rx) + (dy * dy) / (ry * ry) <= 1.0


class CircleShape(EllipseShape):
    TYPE_NAME = "circle"
    DEFAULT_WIDTH = 80.0
    DEFAULT_HEIGHT = 80.0

    def _normalize_size(self, width: float, height: float) -> tuple[float, float]:
        size = max(width, height, self.MIN_SIZE)
        return size, size


class PolygonShape(Shape, ABC):
    def _draw_shape(self, painter: QPainter) -> None:
        painter.save()
        painter.setPen(QPen(QColor("#2d3436"), 2))
        painter.setBrush(self.color)
        painter.drawPolygon(self._polygon())
        painter.restore()

    def contains_point(self, point: QPointF) -> bool:
        path = QPainterPath()
        path.addPolygon(self._polygon())
        return path.contains(point)

    @abstractmethod
    def _polygon(self) -> QPolygonF:
        pass


class TriangleShape(PolygonShape):
    TYPE_NAME = "triangle"
    DEFAULT_WIDTH = 100.0
    DEFAULT_HEIGHT = 90.0

    def _polygon(self) -> QPolygonF:
        rect = self._rect
        return QPolygonF(
            [
                QPointF(rect.center().x(), rect.top()),
                QPointF(rect.left(), rect.bottom()),
                QPointF(rect.right(), rect.bottom()),
            ]
        )


class RhombusShape(PolygonShape):
    TYPE_NAME = "rhombus"
    DEFAULT_WIDTH = 110.0
    DEFAULT_HEIGHT = 90.0

    def _polygon(self) -> QPolygonF:
        rect = self._rect
        return QPolygonF(
            [
                QPointF(rect.center().x(), rect.top()),
                QPointF(rect.right(), rect.center().y()),
                QPointF(rect.center().x(), rect.bottom()),
                QPointF(rect.left(), rect.center().y()),
            ]
        )


class LineShape(Shape):
    TYPE_NAME = "line"
    DEFAULT_WIDTH = 110.0
    DEFAULT_HEIGHT = 70.0
    MIN_SIZE = 20.0

    def _draw_shape(self, painter: QPainter) -> None:
        painter.save()
        painter.setPen(QPen(self.color, 4))
        painter.drawLine(self._rect.topLeft(), self._rect.bottomRight())
        painter.restore()

    def contains_point(self, point: QPointF) -> bool:
        line = QLineF(self._rect.topLeft(), self._rect.bottomRight())
        return self._distance_to_segment(line, point) <= 7.0

    def selection_rect(self) -> QRectF:
        return self._rect.adjusted(-8.0, -8.0, 8.0, 8.0)

    @staticmethod
    def _distance_to_segment(line: QLineF, point: QPointF) -> float:
        dx = line.x2() - line.x1()
        dy = line.y2() - line.y1()
        if math.isclose(dx, 0.0) and math.isclose(dy, 0.0):
            return math.hypot(point.x() - line.x1(), point.y() - line.y1())

        factor = ((point.x() - line.x1()) * dx + (point.y() - line.y1()) * dy) / (dx * dx + dy * dy)
        factor = max(0.0, min(1.0, factor))
        x = line.x1() + factor * dx
        y = line.y1() + factor * dy
        return math.hypot(point.x() - x, point.y() - y)


class GroupShape(Shape):
    TYPE_NAME = "group"
    SELECTION_MARGIN = 6.0

    def __init__(self, children: Iterable[Shape] | None = None) -> None:
        super().__init__(QRectF())
        self._children: list[Shape] = list(children or [])
        for child in self._children:
            child.set_selected(False)
        self._refresh_rect()

    def _draw_shape(self, painter: QPainter) -> None:
        for child in self._children:
            child.draw(painter)

    def contains_point(self, point: QPointF) -> bool:
        return self.selection_rect().contains(point)

    @property
    def color(self) -> QColor:
        return QColor("#000000")

    @color.setter
    def color(self, color: QColor) -> None:
        for child in self._children:
            child.color = color

    def move_by(self, dx: float, dy: float, bounds: QRectF) -> None:
        if not self._children:
            return

        current = self.rect()
        fitted = self._fit_into(bounds, current.translated(dx, dy))
        actual_dx = fitted.left() - current.left()
        actual_dy = fitted.top() - current.top()

        for child in self._children:
            child.move_by(actual_dx, actual_dy, bounds)
        self._refresh_rect()

    def resize_by(self, delta: float, bounds: QRectF) -> None:
        if not self._children:
            return

        current = self.rect()
        max_side = max(current.width(), current.height())
        if max_side <= 0:
            return

        scale = max((max_side + delta) / max_side, self._minimal_scale())
        scale = self._limit_scale(scale, current, bounds)

        origin = current.center()
        for child in self._children:
            child.scale_from(origin, scale, bounds)
        self._refresh_rect()
        self.ensure_inside(bounds)

    def scale_from(self, origin: QPointF, scale: float, bounds: QRectF) -> None:
        for child in self._children:
            child.scale_from(origin, scale, bounds)
        self._refresh_rect()

    def ensure_inside(self, bounds: QRectF) -> None:
        if not self._children:
            return

        current = self.rect()
        if current.width() > bounds.width() or current.height() > bounds.height():
            scale = min(bounds.width() / current.width(), bounds.height() / current.height())
            for child in self._children:
                child.scale_from(current.center(), scale, bounds)
            self._refresh_rect()

        current = self.rect()
        fitted = self._fit_into(bounds, current)
        self.move_by(fitted.left() - current.left(), fitted.top() - current.top(), bounds)

    def can_ungroup(self) -> bool:
        return bool(self._children)

    def take_children(self) -> list[Shape]:
        children = self._children
        self._children = []
        for child in children:
            child.set_selected(True)
        self._refresh_rect()
        return children

    def save(self) -> dict[str, Any]:
        return {
            "type": self.type_name(),
            "rect": _rect_to_list(self.rect()),
            "children": [child.save() for child in self._children],
        }

    def load(self, data: dict[str, Any], factory: "ShapeFactory") -> None:
        children_data = data.get("children")
        if not isinstance(children_data, list):
            raise ValueError("У группы отсутствует список children")

        self._children = []
        for child_data in children_data:
            if not isinstance(child_data, dict):
                raise ValueError("Описание дочернего объекта группы должно быть словарем")
            child_type = str(child_data.get("type", ""))
            child = factory.create(child_type)
            child.load(child_data, factory)
            child.set_selected(False)
            self._children.append(child)

        self._selected = False
        self._refresh_rect()

    def _refresh_rect(self) -> None:
        if not self._children:
            self._rect = QRectF()
            return

        rect = self._children[0].rect()
        for child in self._children[1:]:
            rect = rect.united(child.rect())
        self._rect = rect

    def _minimal_scale(self) -> float:
        scale = 0.01
        for child in self._children:
            rect = child.rect()
            if rect.width() > 0:
                scale = max(scale, child.MIN_SIZE / rect.width())
            if rect.height() > 0:
                scale = max(scale, child.MIN_SIZE / rect.height())
        return scale

    @staticmethod
    def _limit_scale(scale: float, rect: QRectF, bounds: QRectF) -> float:
        if scale <= 1.0:
            return scale

        center = rect.center()
        max_width = 2 * min(center.x() - bounds.left(), bounds.right() - center.x())
        max_height = 2 * min(center.y() - bounds.top(), bounds.bottom() - center.y())
        if rect.width() <= 0 or rect.height() <= 0:
            return scale
        return min(scale, max_width / rect.width(), max_height / rect.height())


class ShapeFactory:
    def __init__(self) -> None:
        self._classes: dict[str, type[Shape]] = {}

    def register(self, shape_class: type[Shape]) -> None:
        self._classes[shape_class.type_name()] = shape_class

    def create(self, shape_type: str) -> Shape:
        shape_class = self._classes.get(shape_type)
        if shape_class is None:
            raise ValueError(f"Неизвестный тип объекта: {shape_type}")
        return shape_class()

    def create_at(self, shape_type: str, center: QPointF, bounds: QRectF) -> Shape:
        shape = self.create(shape_type)
        shape.place_at(center, bounds)
        return shape

    @classmethod
    def default(cls) -> "ShapeFactory":
        factory = cls()
        for shape_class in (
            CircleShape,
            SquareShape,
            EllipseShape,
            RectangleShape,
            TriangleShape,
            LineShape,
            RhombusShape,
            GroupShape,
        ):
            factory.register(shape_class)
        return factory
