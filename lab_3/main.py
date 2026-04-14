import math
import sys

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QColor, QKeyEvent, QMouseEvent, QPaintEvent, QPainter, QPen, QResizeEvent
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget


class CCircle:
    RADIUS = 30

    def __init__(self, x: int, y: int) -> None:
        self._center = QPoint(x, y)
        self._selected = False

    def draw(self, painter: QPainter) -> None:
        fill_color = QColor("#0000ff") if self._selected else QColor("#000000")
        border_color = QColor("#ff0000") if self._selected else QColor("#808080")
        painter.setPen(QPen(border_color, 2))
        painter.setBrush(fill_color)
        painter.drawEllipse(self._center, self.RADIUS, self.RADIUS)

    def contains_point(self, point: QPoint) -> bool:
        dx = point.x() - self._center.x()
        dy = point.y() - self._center.y()
        return math.hypot(dx, dy) <= self.RADIUS

    def set_selected(self, selected: bool) -> None:
        self._selected = selected

    def is_selected(self) -> bool:
        return self._selected


class CircleStorage:
    def __init__(self) -> None:
        self._circles: list[CCircle] = []
        self._iter_index = 0

    def add(self, circle: CCircle) -> None:
        self._circles.append(circle)

    def clear_selection(self) -> None:
        for circle in self._circles:
            circle.set_selected(False)

    def remove_selected(self) -> None:
        self._circles = [circle for circle in self._circles if not circle.is_selected()]
        self._iter_index = 0

    def hit_test(self, point: QPoint) -> list[CCircle]:
        return [circle for circle in reversed(self._circles) if circle.contains_point(point)]

    def count(self) -> int:
        return len(self._circles)

    def __len__(self):
        return len(self._circles)

    def __iter__(self):
        for c in self._circles:
            yield c

    def get_object(self) -> CCircle:
        return self._circles[self._iter_index]


class PaintArea(QWidget):
    def __init__(self, storage: CircleStorage, status_label: QLabel, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._storage = storage
        self._status_label = status_label
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True)
        self._update_status()

    def paintEvent(self, event: QPaintEvent) -> None:
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor("#ffffff"))

        for circle in self._storage:
            circle.draw(painter)


    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() != Qt.LeftButton:
            return

        self.setFocus()
        point = event.position().toPoint()
        hit_circles = self._storage.hit_test(point)
        ctrl_pressed = bool(event.modifiers() & Qt.ControlModifier)

        if hit_circles:
            top_circle = hit_circles[0]
            if ctrl_pressed:
                top_circle.set_selected(not top_circle.is_selected())
            else:
                self._storage.clear_selection()
                top_circle.set_selected(True)
        else:
            if not ctrl_pressed:
                self._storage.clear_selection()
            self._storage.add(CCircle(point.x(), point.y()))

        self._update_status()
        self.update()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Delete:
            self._storage.remove_selected()
            self._update_status()
            self.update()
            event.accept()
            return

        super().keyPressEvent(event)

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self._update_status()

    def _update_status(self) -> None:
        self._status_label.setText(f"Кругов: {self._storage.count()}")


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Круги на форме")
        self.setMinimumSize(400, 300)
        self._storage = CircleStorage()
        self._init_ui()

    def _init_ui(self) -> None:
        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        status_label = QLabel(self)

        paint_area = PaintArea(self._storage, status_label, self)
        layout.addWidget(paint_area, 1)
        layout.addWidget(status_label)

        self.setCentralWidget(central_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
