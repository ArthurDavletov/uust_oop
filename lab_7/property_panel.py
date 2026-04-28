from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Any, Callable

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from shape_storage import ShapeStorage
from shapes import Shape


@dataclass(frozen=True)
class ReflectedProperty:
    name: str
    label: str
    order: int
    editable: bool
    editor_kind: str
    value: Any


def reflected_properties(shape: Shape) -> list[ReflectedProperty]:
    properties: list[ReflectedProperty] = []
    for name, descriptor in inspect.getmembers(type(shape), lambda member: isinstance(member, property)):
        getter = descriptor.fget
        if getter is None or not hasattr(getter, "_inspector_label"):
            continue
        properties.append(
            ReflectedProperty(
                name=name,
                label=str(getattr(getter, "_inspector_label")),
                order=int(getattr(getter, "_inspector_order", 100)),
                editable=bool(getattr(getter, "_inspector_editable", False)),
                editor_kind=str(getattr(getter, "_inspector_editor", "auto")),
                value=getattr(shape, name),
            )
        )
    return sorted(properties, key=lambda item: (item.order, item.label, item.name))


class PropertiesPanel(QWidget):
    def __init__(
        self,
        storage: ShapeStorage,
        apply_property_change: Callable[[str, str, Any, str], bool],
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._storage = storage
        self._storage.add_observer(self)
        self._apply_property_change = apply_property_change
        self._current_object_id: str | None = None

        self._title_label = QLabel("Свойства", self)
        self._title_label.setStyleSheet("font-weight: 600;")
        self._hint_label = QLabel(self)
        self._hint_label.setWordWrap(True)
        self._form_widget = QWidget(self)
        self._form_layout = QFormLayout(self._form_widget)
        self._form_layout.setContentsMargins(0, 0, 0, 0)
        self._form_layout.setSpacing(8)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        layout.addWidget(self._title_label)
        layout.addWidget(self._hint_label)
        layout.addWidget(self._form_widget, 1)

        self.refresh()

    def storage_changed(self, storage: ShapeStorage, reason: str) -> None:
        del storage, reason
        self.refresh()

    def refresh(self) -> None:
        self._clear_form()

        selected_shapes = self._storage.selected_shapes()
        if len(selected_shapes) != 1:
            self._current_object_id = None
            self._title_label.setText("Свойства")
            self._hint_label.setText("Выберите один объект, чтобы увидеть и изменить его свойства.")
            return

        shape = selected_shapes[0]
        self._current_object_id = shape.object_id()
        self._title_label.setText(shape.display_name())
        self._hint_label.setText("Ниже перечислены свойства объекта.")

        for prop in reflected_properties(shape):
            value_widget = self._create_value_widget(prop)
            self._form_layout.addRow(f"{prop.label}:", value_widget)

    def _create_value_widget(self, prop: ReflectedProperty) -> QWidget:
        if not prop.editable:
            label = QLabel(str(prop.value), self)
            label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            return label

        if prop.editor_kind == "color":
            return self._create_color_editor(prop)

        if isinstance(prop.value, bool):
            editor = QCheckBox(self)
            editor.setChecked(bool(prop.value))
            editor.toggled.connect(lambda checked, p=prop: self._commit_change(p, checked))
            return editor

        if isinstance(prop.value, int) and not isinstance(prop.value, bool):
            editor = QSpinBox(self)
            editor.setRange(-100000, 100000)
            editor.setValue(int(prop.value))
            editor.setKeyboardTracking(False)
            editor.editingFinished.connect(lambda p=prop, e=editor: self._commit_change(p, e.value()))
            return editor

        if isinstance(prop.value, float):
            editor = QDoubleSpinBox(self)
            editor.setDecimals(3)
            editor.setSingleStep(1.0)
            editor.setRange(-100000.0, 100000.0)
            editor.setValue(float(prop.value))
            editor.setKeyboardTracking(False)
            editor.editingFinished.connect(lambda p=prop, e=editor: self._commit_change(p, e.value()))
            return editor

        editor = QLineEdit(str(prop.value), self)
        editor.editingFinished.connect(lambda p=prop, e=editor: self._commit_change(p, e.text()))
        return editor

    def _create_color_editor(self, prop: ReflectedProperty) -> QWidget:
        container = QWidget(self)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        editor = QLineEdit(str(prop.value), container)
        button = QPushButton("...", container)
        button.setFixedWidth(34)

        editor.editingFinished.connect(lambda p=prop, e=editor: self._commit_change(p, e.text()))
        button.clicked.connect(lambda checked=False, p=prop, e=editor: self._choose_color(p, e))

        layout.addWidget(editor, 1)
        layout.addWidget(button)
        return container

    def _choose_color(self, prop: ReflectedProperty, editor: QLineEdit) -> None:
        color = QColorDialog.getColor(QColor(editor.text().strip() or "#4f86f7"), self, "Выбор цвета")
        if not color.isValid():
            return
        editor.setText(color.name())
        self._commit_change(prop, color.name())

    def _commit_change(self, prop: ReflectedProperty, value: Any) -> None:
        if self._current_object_id is None:
            return

        try:
            self._apply_property_change(self._current_object_id, prop.name, value, prop.label)
        except ValueError as error:
            QMessageBox.warning(self, "Ошибка изменения свойства", str(error))

    def _clear_form(self) -> None:
        while self._form_layout.rowCount():
            self._form_layout.removeRow(0)
