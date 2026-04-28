from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QColor
from PySide6.QtWidgets import (
    QApplication,
    QColorDialog,
    QComboBox,
    QDockWidget,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from command_history import CommandHistoryView
from paint_area import PaintArea
from property_panel import PropertiesPanel
from shape_storage import ShapeStorage
from storage_tree import StorageTreeView


class MainWindow(QMainWindow):
    SHAPES = {
        "circle": "Круг",
        "square": "Квадрат",
        "ellipse": "Эллипс",
        "rectangle": "Прямоугольник",
        "triangle": "Треугольник",
        "line": "Отрезок",
        "rhombus": "Ромб",
    }

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Лабораторная работа 7")
        self.setMinimumSize(980, 560)

        self._storage = ShapeStorage()
        self._paint_area = PaintArea(self._storage, self)
        self._tree_widget = StorageTreeView(self._storage, self)
        self._shape_combo = QComboBox(self)
        self._properties_panel = PropertiesPanel(self._storage, self._paint_area.change_object_property, self)
        self._command_history_view = CommandHistoryView(self._paint_area.command_stack(), self)

        self._open_action: QAction | None = None
        self._save_action: QAction | None = None
        self._color_action: QAction | None = None
        self._delete_action: QAction | None = None
        self._copy_action: QAction | None = None
        self._cut_action: QAction | None = None
        self._paste_action: QAction | None = None
        self._clear_action: QAction | None = None
        self._select_all_action: QAction | None = None
        self._undo_action: QAction | None = None
        self._group_action: QAction | None = None
        self._ungroup_action: QAction | None = None
        self._arrow_action: QAction | None = None
        self._bidirectional_arrow_action: QAction | None = None
        self._exit_action: QAction | None = None

        self._init_ui()
        self._paint_area.selectionChanged.connect(self._update_selection_actions)
        self._paint_area.undoAvailabilityChanged.connect(self._update_undo_action)
        self._paint_area.clipboardAvailabilityChanged.connect(self._update_paste_action)
        self._paint_area.arrowModeChanged.connect(self._update_arrow_mode)
        self._tree_widget.selectionRequested.connect(self._paint_area.set_selection)
        self._update_selection_actions(False)
        self._update_undo_action(False)
        self._update_paste_action(False)
        self.statusBar().showMessage("Готово")

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

        splitter = QSplitter(Qt.Horizontal, self)
        splitter.addWidget(self._tree_widget)
        splitter.addWidget(self._paint_area)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([260, 700])
        layout.addWidget(splitter, 1)

        self.setCentralWidget(central_widget)
        self._create_actions()
        self._create_menu()
        self._create_toolbar()
        self._create_docks()
        self._change_shape()
        self._paint_area.setFocus()

    def _create_actions(self) -> None:
        self._open_action = QAction("Загрузить...", self)
        self._open_action.setShortcut("Ctrl+O")
        self._open_action.triggered.connect(self._load_project)

        self._save_action = QAction("Сохранить...", self)
        self._save_action.setShortcut("Ctrl+S")
        self._save_action.triggered.connect(self._save_project)

        self._undo_action = QAction("Отменить", self)
        self._undo_action.setShortcut("Ctrl+Z")
        self._undo_action.triggered.connect(self._paint_area.undo)

        self._color_action = QAction("Цвет...", self)
        self._color_action.setShortcut("Ctrl+L")
        self._color_action.triggered.connect(self._choose_color)

        self._delete_action = QAction("Удалить", self)
        self._delete_action.setShortcut("Delete")
        self._delete_action.triggered.connect(self._paint_area.delete_selected)

        self._copy_action = QAction("Копировать", self)
        self._copy_action.setShortcut("Ctrl+C")
        self._copy_action.triggered.connect(self._paint_area.copy_selected)

        self._cut_action = QAction("Вырезать", self)
        self._cut_action.setShortcut("Ctrl+X")
        self._cut_action.triggered.connect(self._paint_area.cut_selected)

        self._paste_action = QAction("Вставить", self)
        self._paste_action.setShortcut("Ctrl+V")
        self._paste_action.triggered.connect(self._paint_area.paste_clipboard)

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

        self._arrow_action = QAction("Стрелка", self)
        self._arrow_action.setShortcut("Ctrl+R")
        self._arrow_action.setCheckable(True)
        self._arrow_action.triggered.connect(self._toggle_arrow_mode)

        self._bidirectional_arrow_action = QAction("Двунаправленная стрелка", self)
        self._bidirectional_arrow_action.setShortcut("Ctrl+Shift+R")
        self._bidirectional_arrow_action.setCheckable(True)
        self._bidirectional_arrow_action.triggered.connect(self._toggle_bidirectional_arrow_mode)

        self._exit_action = QAction("Выход", self)
        self._exit_action.setShortcut("Alt+F4")
        self._exit_action.triggered.connect(self.close)

    def _create_menu(self) -> None:
        file_menu = self.menuBar().addMenu("Файл")
        file_menu.addAction(self._open_action)
        file_menu.addAction(self._save_action)
        file_menu.addSeparator()
        file_menu.addAction(self._exit_action)

        edit_menu = self.menuBar().addMenu("Правка")
        edit_menu.addAction(self._undo_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self._copy_action)
        edit_menu.addAction(self._cut_action)
        edit_menu.addAction(self._paste_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self._select_all_action)
        edit_menu.addAction(self._clear_action)
        edit_menu.addAction(self._delete_action)

    def _create_toolbar(self) -> None:
        toolbar = QToolBar("Редактирование", self)
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        toolbar.addAction(self._undo_action)
        toolbar.addSeparator()
        toolbar.addAction(self._select_all_action)
        toolbar.addAction(self._clear_action)
        toolbar.addAction(self._copy_action)
        toolbar.addAction(self._cut_action)
        toolbar.addAction(self._paste_action)
        toolbar.addSeparator()
        toolbar.addAction(self._group_action)
        toolbar.addAction(self._ungroup_action)
        toolbar.addAction(self._arrow_action)
        toolbar.addAction(self._bidirectional_arrow_action)
        toolbar.addSeparator()
        toolbar.addAction(self._color_action)
        toolbar.addAction(self._delete_action)

    def _create_docks(self) -> None:
        properties_dock = QDockWidget("Свойства", self)
        properties_dock.setObjectName("properties_dock")
        properties_dock.setWidget(self._properties_panel)
        properties_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, properties_dock)

        history_dock = QDockWidget("История команд", self)
        history_dock.setObjectName("history_dock")
        history_dock.setWidget(self._command_history_view)
        history_dock.setAllowedAreas(Qt.BottomDockWidgetArea | Qt.TopDockWidgetArea)
        self.addDockWidget(Qt.BottomDockWidgetArea, history_dock)

    def _change_shape(self) -> None:
        shape_type = self._shape_combo.currentData()
        self._paint_area.set_shape_type(shape_type)

    def _toggle_arrow_mode(self, checked: bool) -> None:
        if checked:
            self._paint_area.start_arrow_creation(False)
        else:
            self._paint_area.cancel_arrow_creation()

    def _toggle_bidirectional_arrow_mode(self, checked: bool) -> None:
        if checked:
            self._paint_area.start_arrow_creation(True)
        else:
            self._paint_area.cancel_arrow_creation()

    def _save_project(self) -> None:
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Сохранить проект",
            "",
            "Текстовый проект (*.txt);;JSON (*.json);;Все файлы (*)",
        )
        if not file_path:
            return

        path = Path(file_path)
        if not path.suffix:
            suffix = ".json" if selected_filter.startswith("JSON") else ".txt"
            path = path.with_suffix(suffix)

        try:
            self._paint_area.save_to_file(str(path))
        except (OSError, ValueError) as error:
            QMessageBox.warning(self, "Ошибка сохранения", str(error))

    def _load_project(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Загрузить проект",
            "",
            "Текстовый проект (*.txt);;JSON (*.json);;Все файлы (*)",
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
        self._copy_action.setEnabled(has_selection)
        self._cut_action.setEnabled(has_selection)
        self._group_action.setEnabled(self._paint_area.can_group_selection())
        self._ungroup_action.setEnabled(self._paint_area.can_ungroup_selection())

    def _update_undo_action(self, can_undo: bool) -> None:
        self._undo_action.setEnabled(can_undo)

    def _update_paste_action(self, can_paste: bool) -> None:
        self._paste_action.setEnabled(can_paste)

    def _update_arrow_mode(self, active: bool, message: str, bidirectional: bool) -> None:
        self._arrow_action.blockSignals(True)
        self._arrow_action.setChecked(active and not bidirectional)
        self._arrow_action.blockSignals(False)
        self._bidirectional_arrow_action.blockSignals(True)
        self._bidirectional_arrow_action.setChecked(active and bidirectional)
        self._bidirectional_arrow_action.blockSignals(False)

        if active:
            self.statusBar().showMessage(message or "Режим создания стрелки")
        else:
            self.statusBar().showMessage("Готово", 3000)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
