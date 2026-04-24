from __future__ import annotations

import math
import uuid
from abc import ABC, abstractmethod
from typing import Any, Iterable, Mapping, Protocol

from PySide6.QtCore import QLineF, QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen, QPolygonF

__all__ = (
    "MoveContext",
    "Shape",
    "RectangleShape",
    "SquareShape",
    "EllipseShape",
    "CircleShape",
    "TriangleShape",
    "RhombusShape",
    "LineShape",
    "GroupShape",
    "ArrowLink",
    "ShapeFactory",
)


def _format_number(value: float) -> str:
    return f"{value:.3f}".rstrip("0").rstrip(".")


def _format_rect(rect: QRectF) -> str:
    return " ".join(_format_number(value) for value in (rect.left(), rect.top(), rect.width(), rect.height()))


def _rect_to_data(rect: QRectF) -> list[float]:
    return [
        round(rect.left(), 3),
        round(rect.top(), 3),
        round(rect.width(), 3),
        round(rect.height(), 3),
    ]


def _rect_from_list(values: list[int | float | str]) -> QRectF:
    if len(values) != 4:
        raise ValueError("Прямоугольник должен содержать 4 числа: x, y, width, height")
    return QRectF(float(values[0]), float(values[1]), float(values[2]), float(values[3]))


def _load_color(data: dict[str, Any], default: str) -> QColor:
    color = QColor(str(data.get("color", default)))
    if not color.isValid():
        raise ValueError("Некорректный цвет объекта")
    return color


def _load_object_id(data: dict[str, Any]) -> str:
    object_id = str(data.get("id", "")).strip()
    return object_id or uuid.uuid4().hex


def inspector_property(label: str, order: int, *, editable: bool = False, editor: str = "auto"):
    def decorate(func):
        func._inspector_label = label
        func._inspector_order = order
        func._inspector_editable = editable
        func._inspector_editor = editor
        return func

    return decorate


def _rects_equal(first: QRectF, second: QRectF) -> bool:
    return (
        math.isclose(first.left(), second.left())
        and math.isclose(first.top(), second.top())
        and math.isclose(first.width(), second.width())
        and math.isclose(first.height(), second.height())
    )


class MovementObserver(Protocol):
    def source_moved(
        self,
        source: "Shape",
        dx: float,
        dy: float,
        bounds: QRectF,
        context: "MoveContext",
    ) -> None:
        pass


class MoveContext:
    def __init__(self, moved_ids: Iterable[str] | None = None) -> None:
        self._moved_ids = set(moved_ids or [])

    def remember(self, object_id: str) -> None:
        self._moved_ids.add(object_id)

    def has_moved(self, object_id: str) -> bool:
        return object_id in self._moved_ids


class Shape(ABC):
    TYPE_NAME = "shape"
    DISPLAY_NAME = "Объект"
    DEFAULT_WIDTH = 90.0
    DEFAULT_HEIGHT = 70.0
    MIN_SIZE = 24.0
    SELECTION_MARGIN = 4.0
    DEFAULT_COLOR = "#7070ff"

    def __init__(self, rect: QRectF | None = None, object_id: str | None = None) -> None:
        self._rect = QRectF(rect) if rect is not None else QRectF(0, 0, self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT)
        self._color = QColor(self.DEFAULT_COLOR)
        self._selected = False
        self._object_id = object_id or uuid.uuid4().hex
        self._move_observers: list[MovementObserver] = []

    @classmethod
    def create_at(cls, center: QPointF, bounds: QRectF) -> "Shape":
        shape = cls()
        shape.place_at(center, bounds)
        return shape

    @classmethod
    def type_name(cls) -> str:
        return cls.TYPE_NAME

    def object_id(self) -> str:
        return self._object_id

    def short_id(self) -> str:
        return self._object_id[:8]

    def display_name(self) -> str:
        return f"{self.DISPLAY_NAME} {self.short_id()}"

    def details_text(self) -> str:
        return ""

    @property
    @inspector_property("ID", 0)
    def object_id_text(self) -> str:
        return self.object_id()

    @property
    @inspector_property("Тип", 1)
    def type_text(self) -> str:
        return self.type_name()

    @property
    @inspector_property("Название", 2)
    def display_name_text(self) -> str:
        return self.display_name()

    @property
    @inspector_property("X", 10, editable=True)
    def x(self) -> float:
        return round(self._rect.left(), 3)

    @property
    @inspector_property("Y", 11, editable=True)
    def y(self) -> float:
        return round(self._rect.top(), 3)

    @property
    @inspector_property("Ширина", 12, editable=True)
    def width(self) -> float:
        return round(self._rect.width(), 3)

    @property
    @inspector_property("Высота", 13, editable=True)
    def height(self) -> float:
        return round(self._rect.height(), 3)

    @property
    @inspector_property("Цвет", 14, editable=True, editor="color")
    def color_hex(self) -> str:
        return self.color.name()

    def children(self) -> list["Shape"]:
        return []

    def is_link(self) -> bool:
        return False

    def can_create_links(self) -> bool:
        return not self.is_link()

    def add_move_observer(self, observer: MovementObserver) -> None:
        if observer not in self._move_observers:
            self._move_observers.append(observer)

    def remove_move_observer(self, observer: MovementObserver) -> None:
        if observer in self._move_observers:
            self._move_observers.remove(observer)

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

    def move_by(
        self,
        dx: float,
        dy: float,
        bounds: QRectF,
        context: MoveContext | None = None,
    ) -> tuple[float, float]:
        context = context or MoveContext()
        current = QRectF(self._rect)
        fitted = self._fit_into(bounds, current.translated(dx, dy))
        actual_dx = fitted.left() - current.left()
        actual_dy = fitted.top() - current.top()
        if math.isclose(actual_dx, 0.0) and math.isclose(actual_dy, 0.0):
            return 0.0, 0.0

        self._rect = fitted
        context.remember(self.object_id())
        self._notify_moved(actual_dx, actual_dy, bounds, context)
        return actual_dx, actual_dy

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
        current = QRectF(self._rect)
        fitted = self._fit_into(bounds, current)
        self._rect = fitted
        actual_dx = fitted.left() - current.left()
        actual_dy = fitted.top() - current.top()
        if not math.isclose(actual_dx, 0.0) or not math.isclose(actual_dy, 0.0):
            context = MoveContext([self.object_id()])
            self._notify_moved(actual_dx, actual_dy, bounds, context)

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

    def prepare_for_removal(self) -> None:
        pass

    def apply_property_change(self, property_name: str, value: Any, bounds: QRectF) -> bool:
        if property_name == "x":
            dx = float(value) - self._rect.left()
            moved_dx, moved_dy = self.move_by(dx, 0.0, bounds)
            return not math.isclose(moved_dx, 0.0) or not math.isclose(moved_dy, 0.0)
        if property_name == "y":
            dx, dy = self.move_by(0.0, float(value) - self._rect.top(), bounds)
            return not math.isclose(dx, 0.0) or not math.isclose(dy, 0.0)
        if property_name == "width":
            return self._set_rect_geometry(width=float(value), bounds=bounds)
        if property_name == "height":
            return self._set_rect_geometry(height=float(value), bounds=bounds)
        if property_name == "color_hex":
            color = QColor(str(value).strip())
            if not color.isValid():
                raise ValueError("Некорректный цвет. Используйте формат вроде #4f86f7.")
            normalized = color.name()
            if self.color.name() == normalized:
                return False
            self.color = color
            return True
        raise ValueError(f"Свойство {property_name} недоступно для изменения")

    def resolve_references(self, objects_by_id: Mapping[str, "Shape"]) -> None:
        del objects_by_id

    def save(self, indent: int = 0) -> list[str]:
        prefix = "  " * indent
        return [
            f"{prefix}object {self.type_name()}",
            f"{prefix}  id {self.object_id()}",
            f"{prefix}  rect {_format_rect(self._rect)}",
            f"{prefix}  color {self.color.name()}",
            f"{prefix}end",
        ]

    def to_data(self) -> dict[str, Any]:
        return {
            "type": self.type_name(),
            "id": self.object_id(),
            "rect": _rect_to_data(self.rect()),
            "color": self.color.name(),
        }

    def load(self, data: dict[str, Any], factory: "ShapeFactory") -> None:
        del factory
        rect_data = data.get("rect")
        if not isinstance(rect_data, list):
            raise ValueError(f"У объекта {self.type_name()} отсутствует поле rect")

        self._object_id = _load_object_id(data)
        self._rect = _rect_from_list(rect_data)
        self._color = _load_color(data, self.DEFAULT_COLOR)
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

    def _set_rect_geometry(
        self,
        *,
        left: float | None = None,
        top: float | None = None,
        width: float | None = None,
        height: float | None = None,
        bounds: QRectF,
    ) -> bool:
        rect = QRectF(self._rect)
        if left is not None:
            rect.moveLeft(left)
        if top is not None:
            rect.moveTop(top)

        target_width = rect.width() if width is None else max(float(width), self.MIN_SIZE)
        target_height = rect.height() if height is None else max(float(height), self.MIN_SIZE)
        target_width, target_height = self._normalize_size(target_width, target_height)
        rect.setWidth(target_width)
        rect.setHeight(target_height)
        return self._apply_rect(rect, bounds)

    def _apply_rect(self, rect: QRectF, bounds: QRectF) -> bool:
        current = QRectF(self._rect)
        fitted = self._fit_into(bounds, rect)
        if _rects_equal(current, fitted):
            return False

        self._rect = fitted
        dx = fitted.left() - current.left()
        dy = fitted.top() - current.top()
        if not math.isclose(dx, 0.0) or not math.isclose(dy, 0.0):
            context = MoveContext([self.object_id()])
            self._notify_moved(dx, dy, bounds, context)
        return True

    def _notify_moved(self, dx: float, dy: float, bounds: QRectF, context: MoveContext) -> None:
        for observer in list(self._move_observers):
            observer.source_moved(self, dx, dy, bounds, context)


class RectangleShape(Shape):
    TYPE_NAME = "rectangle"
    DISPLAY_NAME = "Прямоугольник"
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
    DISPLAY_NAME = "Квадрат"
    DEFAULT_WIDTH = 80.0
    DEFAULT_HEIGHT = 80.0

    def _normalize_size(self, width: float, height: float) -> tuple[float, float]:
        size = max(width, height, self.MIN_SIZE)
        return size, size


class EllipseShape(Shape):
    TYPE_NAME = "ellipse"
    DISPLAY_NAME = "Эллипс"
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
    DISPLAY_NAME = "Круг"
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
    DISPLAY_NAME = "Треугольник"
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
    DISPLAY_NAME = "Ромб"
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
    DISPLAY_NAME = "Отрезок"
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
    DISPLAY_NAME = "Группа"
    SELECTION_MARGIN = 6.0
    DEFAULT_COLOR = "#000000"

    def __init__(self, children: Iterable[Shape] | None = None, object_id: str | None = None) -> None:
        super().__init__(QRectF(), object_id)
        self._children: list[Shape] = list(children or [])
        for child in self._children:
            child.set_selected(False)
        self._refresh_rect()

    def children(self) -> list["Shape"]:
        return list(self._children)

    def details_text(self) -> str:
        return f"Элементов: {len(self._children)}"

    @property
    @inspector_property("Элементов", 15)
    def children_count(self) -> int:
        return len(self._children)

    def _draw_shape(self, painter: QPainter) -> None:
        for child in self._children:
            child.draw(painter)

    def contains_point(self, point: QPointF) -> bool:
        return self.selection_rect().contains(point)

    @property
    def color(self) -> QColor:
        if not self._children:
            return QColor("#000000")
        return self._children[0].color

    @color.setter
    def color(self, color: QColor) -> None:
        for child in self._children:
            child.color = color

    def move_by(
        self,
        dx: float,
        dy: float,
        bounds: QRectF,
        context: MoveContext | None = None,
    ) -> tuple[float, float]:
        context = context or MoveContext()
        if not self._children:
            return 0.0, 0.0

        current = self.rect()
        fitted = self._fit_into(bounds, current.translated(dx, dy))
        actual_dx = fitted.left() - current.left()
        actual_dy = fitted.top() - current.top()
        if math.isclose(actual_dx, 0.0) and math.isclose(actual_dy, 0.0):
            return 0.0, 0.0

        context.remember(self.object_id())
        for child in self._children:
            child.move_by(actual_dx, actual_dy, bounds, context)
        self._refresh_rect()
        self._notify_moved(actual_dx, actual_dy, bounds, context)
        return actual_dx, actual_dy

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
        self.ensure_inside(bounds)

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

    def take_children(self) -> list["Shape"]:
        children = self._children
        self._children = []
        for child in children:
            child.set_selected(True)
        self._refresh_rect()
        return children

    def apply_property_change(self, property_name: str, value: Any, bounds: QRectF) -> bool:
        if property_name in {"width", "height"}:
            current = self.rect()
            current_size = current.width() if property_name == "width" else current.height()
            if current_size <= 0:
                return False

            target_size = max(float(value), self.MIN_SIZE)
            scale = target_size / current_size
            if math.isclose(scale, 1.0):
                return False

            origin = current.topLeft()
            for child in self._children:
                child.scale_from(origin, scale, bounds)
            self._refresh_rect()
            self.ensure_inside(bounds)
            return True

        return super().apply_property_change(property_name, value, bounds)

    def save(self, indent: int = 0) -> list[str]:
        prefix = "  " * indent
        lines = [
            f"{prefix}object {self.type_name()}",
            f"{prefix}  id {self.object_id()}",
            f"{prefix}  bounds {_format_rect(self.rect())}",
            f"{prefix}  children_count {len(self._children)}",
        ]
        for child in self._children:
            lines.extend(child.save(indent + 1))
        lines.append(f"{prefix}end")
        return lines

    def to_data(self) -> dict[str, Any]:
        return {
            "type": self.type_name(),
            "id": self.object_id(),
            "bounds": _rect_to_data(self.rect()),
            "children_count": len(self._children),
            "children": [child.to_data() for child in self._children],
        }

    def load(self, data: dict[str, Any], factory: "ShapeFactory") -> None:
        children_data = data.get("children", [])
        if not isinstance(children_data, list):
            raise ValueError("У группы отсутствует список children")

        declared_count = data.get("children_count")
        if declared_count is not None and int(declared_count) != len(children_data):
            raise ValueError("Количество дочерних объектов группы не совпадает с children_count")

        self._object_id = _load_object_id(data)
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


class ArrowLink(Shape, MovementObserver):
    TYPE_NAME = "arrow"
    DISPLAY_NAME = "Стрелка"
    DEFAULT_COLOR = "#111111"
    SELECTION_MARGIN = 10.0

    def __init__(
        self,
        source: Shape | None = None,
        target: Shape | None = None,
        object_id: str | None = None,
    ) -> None:
        super().__init__(QRectF(), object_id)
        self._color = QColor(self.DEFAULT_COLOR)
        self._source_id = source.object_id() if source is not None else ""
        self._target_id = target.object_id() if target is not None else ""
        self._source: Shape | None = None
        self._target: Shape | None = None
        self.bind(source, target)

    def is_link(self) -> bool:
        return True

    def can_create_links(self) -> bool:
        return False

    def details_text(self) -> str:
        source_name = self._source.display_name() if self._source is not None else self._source_id[:8]
        target_name = self._target.display_name() if self._target is not None else self._target_id[:8]
        if not source_name and not target_name:
            return ""
        return f"{source_name} -> {target_name}"

    @property
    def x(self) -> float:
        return round(self.rect().left(), 3)

    @property
    def y(self) -> float:
        return round(self.rect().top(), 3)

    @property
    def width(self) -> float:
        return round(self.rect().width(), 3)

    @property
    def height(self) -> float:
        return round(self.rect().height(), 3)

    @property
    @inspector_property("Источник", 10)
    def source_object_text(self) -> str:
        return self._source.display_name() if self._source is not None else self._source_id

    @property
    @inspector_property("Приемник", 11)
    def target_object_text(self) -> str:
        return self._target.display_name() if self._target is not None else self._target_id

    @property
    @inspector_property("Длина", 12)
    def length(self) -> float:
        return round(self._line().length(), 3)

    def source_id(self) -> str:
        return self._source_id

    def target_id(self) -> str:
        return self._target_id

    def bind(self, source: Shape | None, target: Shape | None) -> None:
        if self._source is not None:
            self._source.remove_move_observer(self)

        self._source = source
        self._target = target
        self._source_id = source.object_id() if source is not None else self._source_id
        self._target_id = target.object_id() if target is not None else self._target_id

        if self._source is not None:
            self._source.add_move_observer(self)

    def prepare_for_removal(self) -> None:
        if self._source is not None:
            self._source.remove_move_observer(self)
        self._source = None
        self._target = None

    def resolve_references(self, objects_by_id: Mapping[str, Shape]) -> None:
        source = objects_by_id.get(self._source_id)
        target = objects_by_id.get(self._target_id)
        if source is None or target is None:
            raise ValueError("Стрелка ссылается на несуществующий объект")
        if source.object_id() == target.object_id():
            raise ValueError("Стрелка не может ссылаться объекта сама на себя")
        self.bind(source, target)

    def move_by(
        self,
        dx: float,
        dy: float,
        bounds: QRectF,
        context: MoveContext | None = None,
    ) -> tuple[float, float]:
        del dx, dy, bounds, context
        return 0.0, 0.0

    def resize_by(self, delta: float, bounds: QRectF) -> None:
        del delta, bounds

    def scale_from(self, origin: QPointF, scale: float, bounds: QRectF) -> None:
        del origin, scale, bounds

    def ensure_inside(self, bounds: QRectF) -> None:
        del bounds

    def apply_property_change(self, property_name: str, value: Any, bounds: QRectF) -> bool:
        if property_name == "color_hex":
            return super().apply_property_change(property_name, value, bounds)
        raise ValueError("Для стрелки доступны только свойства просмотра и изменение цвета")

    def rect(self) -> QRectF:
        line = self._line()
        left = min(line.x1(), line.x2())
        top = min(line.y1(), line.y2())
        width = abs(line.x2() - line.x1())
        height = abs(line.y2() - line.y1())
        return QRectF(left, top, width, height)

    def selection_rect(self) -> QRectF:
        return self.rect().adjusted(-self.SELECTION_MARGIN, -self.SELECTION_MARGIN, self.SELECTION_MARGIN, self.SELECTION_MARGIN)

    def contains_point(self, point: QPointF) -> bool:
        return self._distance_to_segment(self._line(), point) <= 8.0

    def save(self, indent: int = 0) -> list[str]:
        prefix = "  " * indent
        return [
            f"{prefix}object {self.type_name()}",
            f"{prefix}  id {self.object_id()}",
            f"{prefix}  color {self.color.name()}",
            f"{prefix}  source {self._source_id}",
            f"{prefix}  target {self._target_id}",
            f"{prefix}end",
        ]

    def to_data(self) -> dict[str, Any]:
        return {
            "type": self.type_name(),
            "id": self.object_id(),
            "color": self.color.name(),
            "source": self._source_id,
            "target": self._target_id,
        }

    def load(self, data: dict[str, Any], factory: "ShapeFactory") -> None:
        del factory
        self._object_id = _load_object_id(data)
        self._color = _load_color(data, self.DEFAULT_COLOR)
        self._selected = False
        self._source_id = str(data.get("source", "")).strip()
        self._target_id = str(data.get("target", "")).strip()
        self._source = None
        self._target = None
        if not self._source_id or not self._target_id:
            raise ValueError("У стрелки должны быть source и target")

    def _draw_shape(self, painter: QPainter) -> None:
        if self._source is None or self._target is None:
            return

        line = self._line()
        if math.isclose(line.length(), 0.0):
            return

        painter.save()
        painter.setPen(QPen(self.color, 3))
        painter.drawLine(line)
        painter.setBrush(self.color)
        painter.drawPolygon(self._arrow_head(line))
        painter.restore()

    def source_moved(
        self,
        source: Shape,
        dx: float,
        dy: float,
        bounds: QRectF,
        context: MoveContext,
    ) -> None:
        if self._source is None or self._target is None:
            return
        if source.object_id() != self._source.object_id():
            return
        if context.has_moved(self._target.object_id()):
            return
        self._target.move_by(dx, dy, bounds, context)

    def _line(self) -> QLineF:
        if self._source is None or self._target is None:
            return QLineF()
        return QLineF(self._source.rect().center(), self._target.rect().center())

    def _arrow_head(self, line: QLineF) -> QPolygonF:
        length = line.length()
        if math.isclose(length, 0.0):
            point = line.p2()
            return QPolygonF([point, point, point])

        dx = (line.x2() - line.x1()) / length
        dy = (line.y2() - line.y1()) / length
        size = 14.0
        back = QPointF(line.x2() - dx * size, line.y2() - dy * size)
        left = QPointF(back.x() - dy * (size * 0.5), back.y() + dx * (size * 0.5))
        right = QPointF(back.x() + dy * (size * 0.5), back.y() - dx * (size * 0.5))
        tip = QPointF(line.x2(), line.y2())
        return QPolygonF([tip, left, right])

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
            ArrowLink,
        ):
            factory.register(shape_class)
        return factory
