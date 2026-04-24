from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Iterator, Protocol

from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QColor

from shapes import ArrowLink, GroupShape, MoveContext, Shape


class AbstractFactory(Protocol):
    def create(self, shape_type: str) -> Shape:
        pass

    def create_at(self, shape_type: str, center: QPointF, bounds: QRectF) -> Shape:
        pass


class ShapeStorageObserver(Protocol):
    def storage_changed(self, storage: "ShapeStorage", reason: str) -> None:
        pass


class ShapeStorage:
    FILE_FORMAT = "uust-oop-lab7"
    LEGACY_FORMATS = {"uust-oop-lab6"}

    def __init__(self) -> None:
        self._shapes: list[Shape] = []
        self._observers: list[ShapeStorageObserver] = []

    def add_observer(self, observer: ShapeStorageObserver) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer: ShapeStorageObserver) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def add(
        self,
        shape: Shape,
        *,
        clear_selection: bool = False,
        select_new: bool = False,
        index: int | None = None,
    ) -> bool:
        if clear_selection:
            self._clear_top_level_selection()
        if select_new:
            shape.set_selected(True)

        if index is None:
            self._shapes.append(shape)
        else:
            self._shapes.insert(index, shape)

        self._cleanup_invalid_links()
        self._notify("structure")
        return True

    def clear(self) -> None:
        if not self._shapes:
            return
        self._detach_links(self._shapes)
        self._shapes.clear()
        self._notify("structure")

    def clear_selection(self) -> bool:
        changed = self._clear_top_level_selection()
        if changed:
            self._notify("selection")
        return changed

    def select_all(self) -> bool:
        changed = False
        for shape in self._shapes:
            if not shape.is_selected():
                shape.set_selected(True)
                changed = True
        if changed:
            self._notify("selection")
        return changed

    def select_only(self, object_id: str) -> bool:
        return self.set_selection([object_id])

    def set_selection(self, object_ids: Iterable[str]) -> bool:
        selected_ids = set(object_ids)
        changed = False
        for shape in self._shapes:
            should_select = shape.object_id() in selected_ids
            if shape.is_selected() != should_select:
                shape.set_selected(should_select)
                changed = True
        if changed:
            self._notify("selection")
        return changed

    def toggle_selection(self, object_id: str) -> bool:
        shape = self.root_object_by_id(object_id)
        if shape is None:
            return False
        shape.set_selected(not shape.is_selected())
        self._notify("selection")
        return True

    def remove_selected(self) -> bool:
        if self.selected_count() == 0:
            return False

        kept: list[Shape] = []
        removed = False
        for shape in self._shapes:
            if shape.is_selected():
                shape.prepare_for_removal()
                removed = True
                continue
            kept.append(shape)

        self._shapes = kept
        self._cleanup_invalid_links()
        if removed:
            self._notify("structure")
        return removed

    def group_selected(self) -> bool:
        selected = [shape for shape in self._shapes if shape.is_selected() and not shape.is_link()]
        if len(selected) < 2:
            return False

        selected_ids = {shape.object_id() for shape in selected}
        first_selected_index = next(
            index for index, shape in enumerate(self._shapes) if shape.object_id() in selected_ids
        )

        self._clear_top_level_selection()
        group = GroupShape(selected)
        group.set_selected(True)

        regrouped: list[Shape] = []
        for index, shape in enumerate(self._shapes):
            if index == first_selected_index:
                regrouped.append(group)
            if shape.object_id() not in selected_ids:
                regrouped.append(shape)

        self._shapes = regrouped
        self._cleanup_invalid_links()
        self._notify("structure")
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

        if not changed:
            return False

        self._shapes = ungrouped
        self._cleanup_invalid_links()
        self._notify("structure")
        return True

    def has_link(self, source_id: str, target_id: str) -> bool:
        for shape in self._shapes:
            if isinstance(shape, ArrowLink) and shape.source_id() == source_id and shape.target_id() == target_id:
                return True
        return False

    def shape_at(self, point: QPointF) -> Shape | None:
        draw_order = list(self.iter_draw_order())
        for shape in reversed(draw_order):
            if shape.contains_point(point):
                return shape
        return None

    def selected_shapes(self) -> list[Shape]:
        return [shape for shape in self._shapes if shape.is_selected()]

    def selected_count(self) -> int:
        return len(self.selected_shapes())

    def groupable_selected_count(self) -> int:
        return len([shape for shape in self._shapes if shape.is_selected() and not shape.is_link()])

    def has_selected_group(self) -> bool:
        return any(shape.is_selected() and shape.can_ungroup() for shape in self._shapes)

    def move_selected(self, allowed_dx: float, allowed_dy: float, bounds: QRectF) -> bool:
        selected = [shape for shape in self._shapes if shape.is_selected() and not shape.is_link()]
        if not selected:
            return False

        for shape in selected:
            rect = shape.rect()
            allowed_dx = min(allowed_dx, bounds.right() - rect.right())
            allowed_dx = max(allowed_dx, bounds.left() - rect.left())
            allowed_dy = min(allowed_dy, bounds.bottom() - rect.bottom())
            allowed_dy = max(allowed_dy, bounds.top() - rect.top())

        if allowed_dx == 0 and allowed_dy == 0:
            return False

        context = MoveContext(shape.object_id() for shape in selected)
        changed = False
        for shape in selected:
            dx, dy = shape.move_by(allowed_dx, allowed_dy, bounds, context)
            changed = changed or dx != 0 or dy != 0

        if changed:
            self._cleanup_invalid_links()
            self._notify("geometry")
        return changed

    def resize_selected(self, delta: float, bounds: QRectF) -> bool:
        before = self.snapshot()
        for shape in self._shapes:
            if shape.is_selected() and not shape.is_link():
                shape.resize_by(delta, bounds)
        if self.snapshot() == before:
            return False
        self._notify("geometry")
        return True

    def recolor_selected(self, color: QColor) -> bool:
        before = self.snapshot()
        for shape in self._shapes:
            if shape.is_selected():
                shape.color = color
        if self.snapshot() == before:
            return False
        self._notify("appearance")
        return True

    def ensure_inside(self, bounds: QRectF) -> bool:
        before = self.snapshot()
        for shape in self._shapes:
            if not shape.is_link():
                shape.ensure_inside(bounds)
        if self.snapshot() == before:
            return False
        self._cleanup_invalid_links()
        self._notify("geometry")
        return True

    def snapshot(self) -> list[dict[str, Any]]:
        snapshot_data: list[dict[str, Any]] = []
        for shape in self._shapes:
            shape_data = shape.to_data()
            shape_data["selected"] = shape.is_selected()
            snapshot_data.append(shape_data)
        return snapshot_data

    def restore_snapshot(self, snapshot_data: list[dict[str, Any]], factory: AbstractFactory) -> None:
        self._load_objects(snapshot_data, factory, restore_selection=True)
        self._notify("structure")

    def save_to_file(self, file_path: str | Path) -> None:
        path = Path(file_path)
        if path.suffix.lower() == ".json":
            self._save_json(path)
            return

        self._save_text(path)

    def load_from_file(self, file_path: str | Path, factory: AbstractFactory) -> None:
        path = Path(file_path)
        text = path.read_text(encoding="utf-8")
        if path.suffix.lower() == ".json" or text.lstrip().startswith("{"):
            objects_data = self._read_json_objects(json.loads(text))
        else:
            parser = TextProjectParser(text)
            objects_data = parser.read_objects({self.FILE_FORMAT, *self.LEGACY_FORMATS})

        self._load_objects(objects_data, factory)
        self._notify("structure")

    def root_object_by_id(self, object_id: str) -> Shape | None:
        for shape in self._shapes:
            if shape.object_id() == object_id:
                return shape
        return None

    def find_by_id(self, object_id: str) -> Shape | None:
        for shape in self._iter_recursive(self._shapes):
            if shape.object_id() == object_id:
                return shape
        return None

    def iter_draw_order(self) -> Iterator[Shape]:
        links = [shape for shape in self._shapes if shape.is_link()]
        others = [shape for shape in self._shapes if not shape.is_link()]
        return iter(links + others)

    def top_level_shapes(self) -> list[Shape]:
        return list(self._shapes)

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
        factory: AbstractFactory,
        restore_selection: bool = False,
    ) -> None:
        self._detach_links(self._shapes)

        loaded_shapes: list[Shape] = []
        for object_data in objects_data:
            shape_type = str(object_data.get("type", ""))
            shape = factory.create(shape_type)
            shape.load(object_data, factory)
            shape.set_selected(bool(object_data.get("selected", False)) if restore_selection else False)
            loaded_shapes.append(shape)

        self._shapes = loaded_shapes
        self._resolve_links()
        self._cleanup_invalid_links(strict=True)

    def _read_json_objects(self, raw_data: Any) -> list[dict[str, Any]]:
        if not isinstance(raw_data, dict):
            raise ValueError("JSON-файл проекта должен содержать объект")
        if raw_data.get("format") not in {self.FILE_FORMAT, *self.LEGACY_FORMATS}:
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

    def _resolve_links(self) -> None:
        objects_by_id = {shape.object_id(): shape for shape in self._iter_recursive(self._shapes)}
        for shape in self._shapes:
            shape.resolve_references(objects_by_id)

    def _cleanup_invalid_links(self, strict: bool = False) -> bool:
        valid_ids = {shape.object_id() for shape in self._iter_recursive(self._shapes)}
        cleaned: list[Shape] = []
        changed = False

        for shape in self._shapes:
            if isinstance(shape, ArrowLink):
                source_missing = shape.source_id() not in valid_ids
                target_missing = shape.target_id() not in valid_ids
                if source_missing or target_missing:
                    shape.prepare_for_removal()
                    changed = True
                    if strict:
                        raise ValueError("Стрелка ссылается на несуществующий объект")
                    continue
            cleaned.append(shape)

        self._shapes = cleaned
        return changed

    def _detach_links(self, shapes: Iterable[Shape]) -> None:
        for shape in shapes:
            shape.prepare_for_removal()
            if shape.children():
                self._detach_links(shape.children())

    def _iter_recursive(self, shapes: Iterable[Shape]) -> Iterator[Shape]:
        for shape in shapes:
            yield shape
            yield from self._iter_recursive(shape.children())

    def _clear_top_level_selection(self) -> bool:
        changed = False
        for shape in self._shapes:
            if shape.is_selected():
                shape.set_selected(False)
                changed = True
        return changed

    def _notify(self, reason: str) -> None:
        for observer in list(self._observers):
            observer.storage_changed(self, reason)

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

    def read_objects(self, expected_formats: str | set[str]) -> list[dict[str, Any]]:
        if isinstance(expected_formats, str):
            allowed_formats = {expected_formats}
        else:
            allowed_formats = set(expected_formats)

        format_line = self._read_tokens("строка формата")
        if len(format_line[1]) != 2 or format_line[1][0] != "format":
            raise self._error(format_line[0], "Ожидалась строка: format <имя_формата>")
        if format_line[1][1] not in allowed_formats:
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
