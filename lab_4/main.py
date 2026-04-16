import math
import sys
from abc import ABC, abstractmethod
from typing import Iterable

from PySide6.QtCore import QLineF, QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QAction, QColor, QKeyEvent, QMouseEvent, QPaintEvent, QPainter, QPainterPath, QPen, QPolygonF, QResizeEvent
from PySide6.QtWidgets import QApplication, QColorDialog, QComboBox, QHBoxLayout, QLabel, QMainWindow, QToolBar, QVBoxLayout, QWidget


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
        return self._color

    @color.setter
    def color(self, color: QColor):
        self._color = color

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

        if width <= 0 or height <= 0:
            return self.MIN_SIZE, self.MIN_SIZE

        scale = min(1.0, max_width / width, max_height / height)
        return width * scale, height * scale


class RectangleShape(Shape):
    DEFAULT_WIDTH = 110.0
    DEFAULT_HEIGHT = 70.0

    def _draw_shape(self, painter: QPainter) -> None:
        painter.save()
        painter.setPen(QPen(QColor("#2d3436"), 2))
        painter.setBrush(self.color)
        painter.drawRect(self.rect())
        painter.restore()

    def contains_point(self, point: QPointF) -> bool:
        return self.rect().contains(point)


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
        painter.drawEllipse(self.rect())
        painter.restore()

    def contains_point(self, point: QPointF) -> bool:
        rect = self.rect()
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
        rect = self.rect()
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
        rect = self.rect()
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


class PaintArea(QWidget):
    selectionChanged = Signal(bool)
    MOVE_STEP = 10
    FAST_MOVE_STEP = 20
    SCALE_STEP = 10
    WORKSPACE_MARGIN = 12.0

    SHAPE_CLASSES = {
        "circle": CircleShape,
        "square": SquareShape,
        "ellipse": EllipseShape,
        "rectangle": RectangleShape,
        "triangle": TriangleShape,
        "line": LineShape,
        "rhombus": RhombusShape,
    }

    def __init__(self, storage: ShapeStorage, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._storage = storage
        self._current_shape = "circle"
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMinimumSize(640, 420)

    def set_shape_type(self, shape_type: str) -> None:
        self._current_shape = shape_type
        self.setFocus()

    def has_selection(self) -> bool:
        return self._storage.selected_count() > 0

    def delete_selected(self) -> None:
        self._storage.remove_selected()
        self._finish_change()

    def clear_selection(self) -> None:
        self._storage.clear_selection()
        self._finish_change()

    def select_all(self) -> None:
        self._storage.select_all()
        self._finish_change()

    def recolor_selected(self, color: QColor) -> None:
        self._storage.recolor_selected(color)
        self._finish_change()

    def paintEvent(self, event: QPaintEvent) -> None:
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor("#dfe6e9"))
        painter.fillRect(self._workspace_rect(), QColor("#ffffff"))
        painter.setPen(QPen(QColor("#95a5a6"), 2))
        painter.drawRect(self._workspace_rect())

        for shape in self._storage:
            shape.draw(painter)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() != Qt.LeftButton:
            return

        self.setFocus()
        point = event.position()
        if not self._workspace_rect().contains(point):
            return

        ctrl_pressed = bool(event.modifiers() & Qt.ControlModifier)
        shape = self._storage.shape_at(point)

        if shape is None:
            self._create_shape(point, ctrl_pressed)
        else:
            self._select_shape(shape, ctrl_pressed)

        self._finish_change()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        step = self.MOVE_STEP
        if event.modifiers() & Qt.ShiftModifier:
            step = self.FAST_MOVE_STEP

        bounds = self._workspace_rect()

        match event.key():
            case Qt.Key_A if event.modifiers() & Qt.ControlModifier:
                self.select_all()
                event.accept()
            case Qt.Key_Delete:
                self.delete_selected()
                event.accept()
            case Qt.Key_Escape:
                self.clear_selection()
                event.accept()
            case Qt.Key_Left:
                self._storage.move_selected(-step, 0, bounds)
                self._finish_change()
                event.accept()
            case Qt.Key_Right:
                self._storage.move_selected(step, 0, bounds)
                self._finish_change()
                event.accept()
            case Qt.Key_Up:
                self._storage.move_selected(0, -step, bounds)
                self._finish_change()
                event.accept()
            case Qt.Key_Down:
                self._storage.move_selected(0, step, bounds)
                self._finish_change()
                event.accept()
            case Qt.Key_Plus | Qt.Key_Equal:
                self._storage.resize_selected(self.SCALE_STEP, bounds)
                self._finish_change()
                event.accept()
            case Qt.Key_Minus:
                self._storage.resize_selected(-self.SCALE_STEP, bounds)
                self._finish_change()
                event.accept()
            case _:
                super().keyPressEvent(event)

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self._storage.ensure_inside(self._workspace_rect())
        self._finish_change()

    def _create_shape(self, point: QPointF, ctrl_pressed: bool) -> None:
        shape_class = self.SHAPE_CLASSES[self._current_shape]
        shape = shape_class.create_at(point, self._workspace_rect())
        if not ctrl_pressed:
            self._storage.clear_selection()
        shape.set_selected(True)
        self._storage.add(shape)

    def _select_shape(self, shape: Shape, ctrl_pressed: bool) -> None:
        if ctrl_pressed:
            shape.set_selected(not shape.is_selected())
            return
        self._storage.clear_selection()
        shape.set_selected(True)

    def _workspace_rect(self) -> QRectF:
        margin = self.WORKSPACE_MARGIN
        return QRectF(self.rect()).adjusted(margin, margin, -margin, -margin)

    def _finish_change(self) -> None:
        self.update()
        self.selectionChanged.emit(self.has_selection())


class MainWindow(QMainWindow):
    SHAPES = {
        "circle": "Круг",
        "square": "Квадрат",
        "ellipse": "Эллипс",
        "rectangle": "Прямоугольник",
        "triangle": "Треугольник",
        "line": "Отрезок",
        "rhombus": "Ромб"
    }

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Лабораторная работа 4. Визуальный редактор")
        self.setMinimumSize(700, 420)

        self._storage = ShapeStorage()
        self._paint_area = PaintArea(self._storage, self)
        self._shape_combo = QComboBox(self)

        self._color_action: QAction | None = None
        self._delete_action: QAction | None = None
        self._clear_action: QAction | None = None
        self._select_all_action: QAction | None = None
        self._exit_action: QAction | None = None

        self._init_ui()
        self._paint_area.selectionChanged.connect(self._update_selection_actions)
        self._update_selection_actions(False)

    def _init_ui(self) -> None:
        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.addWidget(QLabel("Фигура:", self))

        for shape_type, title in self.SHAPES.items():
            self._shape_combo.addItem(title, shape_type)
        self._shape_combo.currentIndexChanged.connect(self._change_shape)

        top_layout.addWidget(self._shape_combo, 1)
        layout.addLayout(top_layout)
        layout.addWidget(self._paint_area, 1)

        self.setCentralWidget(central_widget)
        self._create_actions()
        self._create_menu()
        self._create_toolbar()
        self._change_shape()
        self._paint_area.setFocus()

    def _create_actions(self) -> None:
        self._color_action = QAction("Цвет...", self)
        self._color_action.setShortcut("Ctrl+L")
        self._color_action.triggered.connect(self._choose_color)

        self._delete_action = QAction("Удалить", self)
        self._delete_action.setShortcut("Delete")
        self._delete_action.triggered.connect(self._paint_area.delete_selected)

        self._select_all_action = QAction("Выделить все", self)
        self._select_all_action.setShortcut("Ctrl+A")
        self._select_all_action.triggered.connect(self._paint_area.select_all)

        self._clear_action = QAction("Снять выделение", self)
        self._clear_action.setShortcut("Esc")
        self._clear_action.triggered.connect(self._paint_area.clear_selection)

        self._exit_action = QAction("Выход", self)
        self._exit_action.setShortcut("Alt+F4")
        self._exit_action.triggered.connect(self.close)

    def _create_menu(self) -> None:
        file_menu = self.menuBar().addMenu("Файл")
        file_menu.addAction(self._exit_action)

    def _create_toolbar(self) -> None:
        toolbar = QToolBar("Редактирование", self)
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        toolbar.addAction(self._select_all_action)
        toolbar.addAction(self._clear_action)
        toolbar.addSeparator()
        toolbar.addAction(self._color_action)
        toolbar.addAction(self._delete_action)

    def _change_shape(self) -> None:
        shape_type = self._shape_combo.currentData()
        if shape_type is not None:
            self._paint_area.set_shape_type(shape_type)

    def _choose_color(self) -> None:
        if not self._paint_area.has_selection():
            return
        color = QColorDialog.getColor(QColor("#4f86f7"), self, "Выбор цвета")
        if color.isValid():
            self._paint_area.recolor_selected(color)

    def _update_selection_actions(self, has_selection: bool) -> None:
        self._clear_action.setEnabled(has_selection)
        self._color_action.setEnabled(has_selection)
        self._delete_action.setEnabled(has_selection)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
