from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QKeyEvent, QMouseEvent, QPaintEvent, QPainter, QPen, QResizeEvent
from PySide6.QtWidgets import QWidget

from shape_storage import ShapeStorage
from shapes import *


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