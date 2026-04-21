import json
from pathlib import Path
from typing import Any, Iterable, Protocol

from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QColor

from shapes import GroupShape, Shape


class ShapeFactoryProtocol(Protocol):
    def create(self, shape_type: str) -> Shape:
        pass


class ShapeStorage:
    FILE_FORMAT = "uust-oop-lab6"
    FILE_VERSION = 1

    def __init__(self) -> None:
        self._shapes: list[Shape] = []

    def add(self, shape: Shape) -> None:
        self._shapes.append(shape)

    def clear(self) -> None:
        self._shapes.clear()

    def clear_selection(self) -> None:
        for shape in self._shapes:
            shape.set_selected(False)

    def select_all(self) -> None:
        for shape in self._shapes:
            shape.set_selected(True)

    def remove_selected(self) -> None:
        self._shapes = [shape for shape in self._shapes if not shape.is_selected()]

    def group_selected(self) -> bool:
        selected = self.selected_shapes()
        if len(selected) < 2:
            return False

        selected_ids = {id(shape) for shape in selected}
        first_selected_index = next(
            index for index, shape in enumerate(self._shapes) if id(shape) in selected_ids
        )
        group = GroupShape(selected)
        group.set_selected(True)

        regrouped: list[Shape] = []
        for index, shape in enumerate(self._shapes):
            if index == first_selected_index:
                regrouped.append(group)
            if id(shape) not in selected_ids:
                regrouped.append(shape)

        self._shapes = regrouped
        return True

    def ungroup_selected(self) -> bool:
        changed = False
        ungrouped: list[Shape] = []

        for shape in self._shapes:
            if shape.is_selected() and shape.can_ungroup():
                ungrouped.extend(shape.take_children())
                changed = True
            else:
                ungrouped.append(shape)

        if changed:
            self._shapes = ungrouped
        return changed

    def shape_at(self, point: QPointF) -> Shape | None:
        for shape in reversed(self._shapes):
            if shape.contains_point(point):
                return shape
        return None

    def selected_shapes(self) -> list[Shape]:
        return [shape for shape in self._shapes if shape.is_selected()]

    def selected_count(self) -> int:
        return len(self.selected_shapes())

    def has_selected_group(self) -> bool:
        return any(shape.is_selected() and shape.can_ungroup() for shape in self._shapes)

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

    def save_to_file(self, file_path: str | Path) -> None:
        data = {
            "format": self.FILE_FORMAT,
            "version": self.FILE_VERSION,
            "objects_count": len(self._shapes),
            "objects": [shape.save() for shape in self._shapes],
        }
        Path(file_path).write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def load_from_file(self, file_path: str | Path, factory: ShapeFactoryProtocol) -> None:
        raw_data = json.loads(Path(file_path).read_text(encoding="utf-8"))
        objects_data = self._read_objects(raw_data)

        loaded_shapes: list[Shape] = []
        for object_data in objects_data:
            shape_type = str(object_data.get("type", ""))
            shape = factory.create(shape_type)
            shape.load(object_data, factory)
            shape.set_selected(False)
            loaded_shapes.append(shape)

        self._shapes = loaded_shapes

    def _read_objects(self, raw_data: Any) -> list[dict[str, Any]]:
        if not isinstance(raw_data, dict):
            raise ValueError("Файл проекта должен содержать JSON-объект")
        if raw_data.get("format") != self.FILE_FORMAT:
            raise ValueError("Файл имеет неподдерживаемый формат")
        if int(raw_data.get("version", 0)) != self.FILE_VERSION:
            raise ValueError("Версия файла проекта не поддерживается")

        objects_data = raw_data.get("objects")
        if not isinstance(objects_data, list):
            raise ValueError("В файле отсутствует список objects")

        declared_count = raw_data.get("objects_count")
        if declared_count is not None and int(declared_count) != len(objects_data):
            raise ValueError("Количество объектов в файле не совпадает с objects_count")

        for object_data in objects_data:
            if not isinstance(object_data, dict):
                raise ValueError("Каждый объект в файле должен быть JSON-объектом")
        return objects_data

    def __iter__(self) -> Iterable[Shape]:
        return iter(self._shapes)
