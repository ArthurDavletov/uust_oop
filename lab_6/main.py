import sys
from pathlib import Path

from PySide6.QtGui import QAction, QColor
from PySide6.QtWidgets import (
    QApplication,
    QColorDialog,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from paint_area import PaintArea
from shape_storage import ShapeStorage


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
        self.setWindowTitle("Лабораторная работа 6. Группировка и сохранение")
        self.setMinimumSize(700, 420)

        self._storage = ShapeStorage()
        self._paint_area = PaintArea(self._storage, self)
        self._shape_combo = QComboBox(self)

        self._open_action: QAction | None = None
        self._save_action: QAction | None = None
        self._color_action: QAction | None = None
        self._delete_action: QAction | None = None
        self._clear_action: QAction | None = None
        self._select_all_action: QAction | None = None
        self._group_action: QAction | None = None
        self._ungroup_action: QAction | None = None
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
        self._open_action = QAction("Загрузить...", self)
        self._open_action.setShortcut("Ctrl+O")
        self._open_action.triggered.connect(self._load_project)

        self._save_action = QAction("Сохранить...", self)
        self._save_action.setShortcut("Ctrl+S")
        self._save_action.triggered.connect(self._save_project)

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

        self._group_action = QAction("Сгруппировать", self)
        self._group_action.setShortcut("Ctrl+G")
        self._group_action.triggered.connect(self._paint_area.group_selected)

        self._ungroup_action = QAction("Разгруппировать", self)
        self._ungroup_action.setShortcut("Ctrl+U")
        self._ungroup_action.triggered.connect(self._paint_area.ungroup_selected)

        self._exit_action = QAction("Выход", self)
        self._exit_action.setShortcut("Alt+F4")
        self._exit_action.triggered.connect(self.close)

    def _create_menu(self) -> None:
        file_menu = self.menuBar().addMenu("Файл")
        file_menu.addAction(self._open_action)
        file_menu.addAction(self._save_action)
        file_menu.addSeparator()
        file_menu.addAction(self._exit_action)

    def _create_toolbar(self) -> None:
        toolbar = QToolBar("Редактирование", self)
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        toolbar.addAction(self._select_all_action)
        toolbar.addAction(self._clear_action)
        toolbar.addSeparator()
        toolbar.addAction(self._group_action)
        toolbar.addAction(self._ungroup_action)
        toolbar.addSeparator()
        toolbar.addAction(self._color_action)
        toolbar.addAction(self._delete_action)

    def _change_shape(self) -> None:
        shape_type = self._shape_combo.currentData()
        self._paint_area.set_shape_type(shape_type)

    def _save_project(self) -> None:
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить проект",
            "",
            "JSON (*.json);;Текстовый проект (*.txt);;Все файлы (*)",
        )
        if not file_path:
            return

        path = Path(file_path)
        if not path.suffix:
            path = path.with_suffix(".json")

        try:
            self._paint_area.save_to_file(str(path))
        except (OSError, ValueError) as error:
            QMessageBox.warning(self, "Ошибка сохранения", str(error))

    def _load_project(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Загрузить проект",
            "",
            "JSON (*.json);;Текстовый проект (*.txt);;Все файлы (*)",
        )
        if not file_path:
            return

        try:
            self._paint_area.load_from_file(file_path)
        except (OSError, ValueError) as error:
            QMessageBox.warning(self, "Ошибка загрузки", str(error))

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
        self._group_action.setEnabled(self._paint_area.can_group_selection())
        self._ungroup_action.setEnabled(self._paint_area.can_ungroup_selection())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
