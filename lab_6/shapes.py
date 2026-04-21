import math
from abc import ABC, abstractmethod
from PySide6.QtCore import QLineF, QRectF, QPointF, Qt
from PySide6.QtGui import QColor, QPainter, QPen, QPainterPath, QPolygonF

__all__ = (
    "Shape", "RectangleShape", "SquareShape", "EllipseShape",
    "CircleShape", "TriangleShape", "RhombusShape", "LineShape"
)


class Shape(ABC):
    DEFAULT_WIDTH = 90.0
    DEFAULT_HEIGHT = 70.0
    MIN_SIZE = 24.0
    SELECTION_MARGIN = 4.0

    def __init__(self, rect: QRectF) -> None:
        self._rect = QRectF(rect)
        self._color = QColor("#7070ff")
        self._selected = False

    @classmethod
    def create_at(cls, center: QPointF, bounds: QRectF) -> "Shape":
        rect = QRectF(
            center.x() - cls.DEFAULT_WIDTH / 2,
            center.y() - cls.DEFAULT_HEIGHT / 2,
            cls.DEFAULT_WIDTH,
            cls.DEFAULT_HEIGHT,
        )
        shape = cls(rect)
        shape.ensure_inside(bounds)
        return shape

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

    @property
    def color(self):
        return QColor(self._color)

    @color.setter
    def color(self, color: QColor):
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
    DEFAULT_WIDTH = 80.0
    DEFAULT_HEIGHT = 80.0

    def _normalize_size(self, width: float, height: float) -> tuple[float, float]:
        size = max(width, height, self.MIN_SIZE)
        return size, size


class EllipseShape(Shape):
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
