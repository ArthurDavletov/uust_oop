import sys

from PySide6.QtCore import QObject, QSettings, Qt, Signal
from PySide6.QtGui import QFont, QIntValidator
from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QMainWindow,
    QSizePolicy,
    QSlider,
    QSpinBox,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)


class NumberModel(QObject):
    changed = Signal(int, int, int)

    MIN_VALUE = 0
    MAX_VALUE = 100

    def __init__(self):
        super().__init__()
        self._settings = QSettings("UUST", "Lab3Part2MVC")
        self._a = 0
        self._b = 0
        self._c = 0

    @property
    def minimum(self) -> int:
        return self.MIN_VALUE

    @property
    def maximum(self) -> int:
        return self.MAX_VALUE

    def values(self) -> tuple[int, int, int]:
        return self._a, self._b, self._c

    def initialize(self) -> None:
        loaded = (
            self._read_int("a", 0),
            self._read_int("b", 0),
            self._read_int("c", 0),
        )
        self._apply_values(*self._normalize_loaded(*loaded), emit_even_if_same=True)

    def set_a(self, value: int) -> None:
        value = self._limit_to_range(value)
        a, b, c = self.values()
        a = value
        if b < a:
            b = a
        if c < b:
            c = b
        self._apply_values(a, b, c)

    def set_b(self, value: int) -> None:
        value = self._limit_to_range(value)
        a, _, c = self.values()
        b = value
        if b < a:
            b = a
        if b > c:
            b = c
        self._apply_values(a, b, c)

    def set_c(self, value: int) -> None:
        value = self._limit_to_range(value)
        a, b, c = self.values()
        c = value
        if b > c:
            b = c
        if a > b:
            a = b
        self._apply_values(a, b, c)

    def _read_int(self, key: str, default: int) -> int:
        raw_value = self._settings.value(key, default)
        try:
            return int(raw_value)
        except (TypeError, ValueError):
            return default

    def _limit_to_range(self, value: int) -> int:
        if value < self.MIN_VALUE:
            return self.MIN_VALUE
        if value > self.MAX_VALUE:
            return self.MAX_VALUE
        return value

    def _normalize_loaded(self, a: int, b: int, c: int) -> tuple[int, int, int]:
        a = self._limit_to_range(a)
        b = self._limit_to_range(b)
        c = self._limit_to_range(c)
        if a > c:
            c = a
        if b < a:
            b = a
        if b > c:
            b = c
        return a, b, c

    def _apply_values(self, new_a: int, new_b: int, new_c: int, emit_even_if_same: bool = False) -> None:
        old_values = self.values()
        new_values = (new_a, new_b, new_c)
        if not emit_even_if_same and new_values == old_values:
            return

        self._a, self._b, self._c = new_values
        self._save()
        self.changed.emit(*new_values)

    def _save(self) -> None:
        self._settings.setValue("a", self._a)
        self._settings.setValue("b", self._b)
        self._settings.setValue("c", self._c)
        self._settings.sync()


class IntegerLineEdit(QLineEdit):
    focus_lost = Signal()

    def focusOutEvent(self, event) -> None:
        super().focusOutEvent(event)
        self.focus_lost.emit()


class NumberRow(QObject):
    def __init__(self, name: str, getter, setter, minimum: int, maximum: int):
        super().__init__()
        self.getter = getter
        self.setter = setter

        self.name_label = QLabel(name)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont(self.name_label.font())
        title_font.setPointSize(title_font.pointSize() + 12)
        title_font.setBold(True)
        self.name_label.setFont(title_font)

        self.line_edit = IntegerLineEdit()
        self.line_edit.setValidator(QIntValidator(minimum, maximum, self.line_edit))
        self.line_edit.setPlaceholderText(f"от {minimum} до {maximum}")
        self.line_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.spin_box = QSpinBox()
        self.spin_box.setRange(minimum, maximum)
        self.spin_box.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(minimum, maximum)

        self.line_edit.focus_lost.connect(self._commit_line_edit)
        self.line_edit.returnPressed.connect(self._commit_line_edit)
        self.spin_box.valueChanged.connect(self._commit_num_value)
        self.slider.valueChanged.connect(self._commit_num_value)

    def _commit_line_edit(self) -> None:
        text = self.line_edit.text().strip()
        if not text:
            self.set_value(self.getter())
            return

        try:
            self.setter(int(text))
        except ValueError:
            self.set_value(self.getter())
            return

        self.set_value(self.getter())

    def _commit_num_value(self, value: int) -> None:
        self.setter(value)
        self.set_value(self.getter())

    def set_value(self, value: int) -> None:
        widgets = (self.line_edit, self.spin_box, self.slider)
        blockers = [widget.blockSignals(True) for widget in widgets]

        self.line_edit.setText(str(value))
        self.spin_box.setValue(value)
        self.slider.setValue(value)

        for widget, blocked in zip(widgets, blockers):
            widget.blockSignals(blocked)


class MainWindow(QMainWindow):
    def __init__(self, model: NumberModel):
        super().__init__()
        self.model = model
        self.update_count = 0

        self.setWindowTitle("ЛР №3. Часть 2. MVC")
        self.setMinimumSize(720, 320)

        self.row_a = NumberRow(
            "A",
            lambda: self.model.values()[0],
            self.model.set_a,
            self.model.minimum,
            self.model.maximum,
        )
        self.row_b = NumberRow(
            "B",
            lambda: self.model.values()[1],
            self.model.set_b,
            self.model.minimum,
            self.model.maximum,
        )
        self.row_c = NumberRow(
            "C",
            lambda: self.model.values()[2],
            self.model.set_c,
            self.model.minimum,
            self.model.maximum,
        )

        self.counter_label = QLabel(f"Количество обновлений формы: {self.update_count}")

        self._build_ui()
        self.model.changed.connect(self._refresh_from_model)

    def _build_ui(self) -> None:
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        group = QGroupBox("Числа A, B и C")
        form_layout = QGridLayout(group)
        first_operator_label = QLabel("<=")
        first_operator_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        second_operator_label = QLabel("<=")
        second_operator_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        rows = (self.row_a, self.row_b, self.row_c)
        for column, row in enumerate(rows):
            target_column = column * 2
            form_layout.addWidget(row.name_label, 0, target_column)
            form_layout.addWidget(row.line_edit, 1, target_column)
            form_layout.addWidget(row.spin_box, 2, target_column)
            form_layout.addWidget(row.slider, 3, target_column)

        form_layout.addWidget(first_operator_label, 0, 1)
        form_layout.addWidget(second_operator_label, 0, 3)

        form_layout.setColumnStretch(0, 1)
        form_layout.setColumnStretch(2, 1)
        form_layout.setColumnStretch(4, 1)

        main_layout.addWidget(group)

        status_bar = QStatusBar(self)
        status_bar.setSizeGripEnabled(False)
        status_bar.addWidget(self.counter_label)
        self.setStatusBar(status_bar)

    def _refresh_from_model(self, a: int, b: int, c: int) -> None:
        self.update_count += 1
        print(f"Обновление формы №{self.update_count}: A = {a}, B = {b}, C = {c}")

        self.row_a.set_value(a)
        self.row_b.set_value(b)
        self.row_c.set_value(c)
        self.counter_label.setText(f"Количество обновлений формы: {self.update_count}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    model = NumberModel()
    window = MainWindow(model)
    model.initialize()
    window.show()
    sys.exit(app.exec())
