import json
from pathlib import Path
from typing import Any, Iterable, Protocol

from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QColor

from shapes import GroupShape, Shape


class ShapeFactoryProtocol(Protocol):
    def create(self, shape_type: str) -> Shape:
        pass

    def create_at(self, shape_type: str, center: QPointF, bounds: QRectF) -> Shape:
        pass


class ShapeStorage:
    FILE_FORMAT = "uust-oop-lab6"

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

    def snapshot(self) -> list[dict[str, Any]]:
        snapshot_data: list[dict[str, Any]] = []
        for shape in self._shapes:
            shape_data = shape.to_data()
            shape_data["selected"] = shape.is_selected()
            snapshot_data.append(shape_data)
        return snapshot_data

    def restore_snapshot(self, snapshot_data: list[dict[str, Any]], factory: ShapeFactoryProtocol) -> None:
        self._load_objects(snapshot_data, factory, restore_selection=True)

    def save_to_file(self, file_path: str | Path) -> None:
        path = Path(file_path)
        if path.suffix.lower() == ".json":
            self._save_json(path)
            return

        self._save_text(path)

    def load_from_file(self, file_path: str | Path, factory: ShapeFactoryProtocol) -> None:
        path = Path(file_path)
        text = path.read_text(encoding="utf-8")
        if path.suffix.lower() == ".json" or text.lstrip().startswith("{"):
            objects_data = self._read_json_objects(json.loads(text))
        else:
            parser = TextProjectParser(text)
            objects_data = parser.read_objects(self.FILE_FORMAT)

        self._load_objects(objects_data, factory)

    def _save_text(self, path: Path) -> None:
        lines = [
            f"format {self.FILE_FORMAT}",
            f"objects {len(self._shapes)}",
            "",
        ]
        for shape in self._shapes:
            lines.extend(shape.save())
            lines.append("")

        path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    def _save_json(self, path: Path) -> None:
        data = {
            "format": self.FILE_FORMAT,
            "objects_count": len(self._shapes),
            "objects": [shape.to_data() for shape in self._shapes],
        }
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def _load_objects(
        self,
        objects_data: list[dict[str, Any]],
        factory: ShapeFactoryProtocol,
        restore_selection: bool = False,
    ) -> None:
        loaded_shapes: list[Shape] = []
        for object_data in objects_data:
            shape_type = str(object_data.get("type", ""))
            shape = factory.create(shape_type)
            shape.load(object_data, factory)
            shape.set_selected(bool(object_data.get("selected", False)) if restore_selection else False)
            loaded_shapes.append(shape)

        self._shapes = loaded_shapes

    def _read_json_objects(self, raw_data: Any) -> list[dict[str, Any]]:
        if not isinstance(raw_data, dict):
            raise ValueError("JSON-файл проекта должен содержать объект")
        if raw_data.get("format") != self.FILE_FORMAT:
            raise ValueError("Файл имеет неподдерживаемый формат")

        objects_data = raw_data.get("objects")
        if not isinstance(objects_data, list):
            raise ValueError("В JSON-файле отсутствует список objects")

        declared_count = raw_data.get("objects_count")
        if declared_count is not None and int(declared_count) != len(objects_data):
            raise ValueError("Количество объектов в JSON-файле не совпадает с objects_count")

        for object_data in objects_data:
            if not isinstance(object_data, dict):
                raise ValueError("Каждый объект в JSON-файле должен быть объектом")
        return objects_data

    def __iter__(self) -> Iterable[Shape]:
        return iter(self._shapes)


class TextProjectParser:
    def __init__(self, text: str) -> None:
        self._lines = [
            (line_number, line.strip())
            for line_number, line in enumerate(text.splitlines(), 1)
            if line.strip() and not line.strip().startswith("#")
        ]
        self._position = 0

    def read_objects(self, expected_format: str) -> list[dict[str, Any]]:
        format_line = self._read_tokens("строка формата")
        if len(format_line[1]) != 2 or format_line[1][0] != "format":
            raise self._error(format_line[0], "Ожидалась строка: format <имя_формата>")
        if format_line[1][1] != expected_format:
            raise self._error(format_line[0], "Файл имеет неподдерживаемый формат")

        objects_line = self._read_tokens("количество объектов")
        if len(objects_line[1]) != 2 or objects_line[1][0] != "objects":
            raise self._error(objects_line[0], "Ожидалась строка: objects <количество>")
        objects_count = int(objects_line[1][1])

        objects: list[dict[str, Any]] = []
        while not self._is_finished():
            objects.append(self._read_object())

        if len(objects) != objects_count:
            raise ValueError("Количество объектов в файле не совпадает со строкой objects")
        return objects

    def _read_object(self) -> dict[str, Any]:
        line_number, tokens = self._read_tokens("описание объекта")
        if len(tokens) != 2 or tokens[0] != "object":
            raise self._error(line_number, "Ожидалась строка: object <тип>")

        data: dict[str, Any] = {"type": tokens[1]}
        children: list[dict[str, Any]] = []

        while True:
            if self._is_finished():
                raise self._error(line_number, "Не найден конец объекта: end")

            _, current_tokens = self._peek_tokens()
            if current_tokens == ["end"]:
                self._position += 1
                break
            if current_tokens[0] == "object":
                children.append(self._read_object())
                continue

            self._position += 1
            key = current_tokens[0]
            values = current_tokens[1:]
            if not values:
                data[key] = ""
            elif len(values) == 1:
                data[key] = values[0]
            else:
                data[key] = values

        if children:
            data["children"] = children
        return data

    def _read_tokens(self, description: str) -> tuple[int, list[str]]:
        if self._is_finished():
            raise ValueError(f"Неожиданный конец файла: ожидалось {description}")
        line = self._peek_tokens()
        self._position += 1
        return line

    def _peek_tokens(self) -> tuple[int, list[str]]:
        line_number, line = self._lines[self._position]
        return line_number, line.split()

    def _is_finished(self) -> bool:
        return self._position >= len(self._lines)

    @staticmethod
    def _error(line_number: int, message: str) -> ValueError:
        return ValueError(f"Строка {line_number}: {message}")
