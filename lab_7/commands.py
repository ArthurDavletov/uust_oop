from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Iterable, Protocol

from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QColor

from shape_storage import AbstractFactory, ShapeStorage
from shapes import ArrowLink, Shape


@dataclass(frozen=True)
class CommandHistoryEntry:
    title: str
    is_done: bool
    is_current: bool


class CommandStackObserver(Protocol):
    def history_changed(self, stack: "CommandStack") -> None:
        pass


class Command(ABC):
    def __init__(self, title: str) -> None:
        self._title = title

    @property
    def title(self) -> str:
        return self._title

    @abstractmethod
    def execute(self) -> bool:
        pass

    @abstractmethod
    def undo(self) -> None:
        pass


class CommandStack:
    def __init__(self) -> None:
        self._history: list[Command] = []
        self._cursor = 0
        self._observers: list[CommandStackObserver] = []

    def add_observer(self, observer: CommandStackObserver) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer: CommandStackObserver) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def execute(self, command: Command) -> bool:
        if not command.execute():
            return False

        if self._cursor < len(self._history):
            self._history = self._history[: self._cursor]

        self._history.append(command)
        self._cursor += 1
        self._notify()
        return True

    def push_committed(self, command: Command) -> bool:
        return self.execute(command)

    def undo(self) -> bool:
        if self._cursor == 0:
            return False

        command = self._history[self._cursor - 1]
        command.undo()
        self._cursor -= 1
        self._notify()
        return True

    def can_undo(self) -> bool:
        return self._cursor > 0

    def history_entries(self) -> list[CommandHistoryEntry]:
        entries: list[CommandHistoryEntry] = []
        for index, command in enumerate(self._history):
            is_done = index < self._cursor
            entries.append(
                CommandHistoryEntry(
                    title=command.title,
                    is_done=is_done,
                    is_current=is_done and index == self._cursor - 1,
                )
            )
        return entries

    def _notify(self) -> None:
        for observer in list(self._observers):
            observer.history_changed(self)


class SnapshotCommand(Command):
    def __init__(self, storage: ShapeStorage, factory: AbstractFactory, title: str) -> None:
        super().__init__(title)
        self._storage = storage
        self._factory = factory
        self._before: list[dict[str, Any]] = []

    def execute(self) -> bool:
        self._before = self._storage.snapshot()
        if not self._apply():
            return False
        return self._storage.snapshot() != self._before

    def undo(self) -> None:
        self._storage.restore_snapshot(self._before, self._factory)

    @abstractmethod
    def _apply(self) -> bool:
        pass


class CommittedSnapshotCommand(Command):
    def __init__(
        self,
        storage: ShapeStorage,
        factory: AbstractFactory,
        before: list[dict[str, Any]],
        after: list[dict[str, Any]],
        title: str,
    ) -> None:
        super().__init__(title)
        self._storage = storage
        self._factory = factory
        self._before = before
        self._after = after

    def execute(self) -> bool:
        if self._before == self._after:
            return False
        self._storage.restore_snapshot(self._after, self._factory)
        return True

    def undo(self) -> None:
        self._storage.restore_snapshot(self._before, self._factory)


class CreateShapeCommand(SnapshotCommand):
    def __init__(
        self,
        storage: ShapeStorage,
        factory: AbstractFactory,
        shape_type: str,
        point: QPointF,
        bounds: QRectF,
        keep_selection: bool,
    ) -> None:
        super().__init__(storage, factory, f"Создать объект: {shape_type}")
        self._shape_type = shape_type
        self._point = QPointF(point)
        self._bounds = QRectF(bounds)
        self._keep_selection = keep_selection

    def _apply(self) -> bool:
        shape = self._factory.create_at(self._shape_type, self._point, self._bounds)
        return self._storage.add(shape, clear_selection=not self._keep_selection, select_new=True)


class CreateArrowCommand(SnapshotCommand):
    def __init__(
        self,
        storage: ShapeStorage,
        factory: AbstractFactory,
        source: Shape,
        target: Shape,
        bidirectional: bool = False,
    ) -> None:
        title = "Создать двунаправленную стрелку" if bidirectional else "Создать стрелку"
        super().__init__(storage, factory, title)
        self._source = source
        self._target = target
        self._bidirectional = bidirectional

    def _apply(self) -> bool:
        if self._source.object_id() == self._target.object_id():
            return False

        existing_link = self._storage.link_between(self._source.object_id(), self._target.object_id())
        if existing_link is not None:
            same_direction = (
                existing_link.source_id() == self._source.object_id()
                and existing_link.target_id() == self._target.object_id()
            )
            if self._bidirectional or not same_direction:
                self._title = "Сделать стрелку двунаправленной"
                return self._storage.make_link_bidirectional(self._source.object_id(), self._target.object_id())
            return False

        arrow = ArrowLink(self._source, self._target, self._bidirectional)
        return self._storage.add(arrow, clear_selection=True, select_new=True)


class SetSelectionCommand(SnapshotCommand):
    def __init__(
        self,
        storage: ShapeStorage,
        factory: AbstractFactory,
        object_ids: Iterable[str],
        title: str = "Изменить выделение",
    ) -> None:
        super().__init__(storage, factory, title)
        self._object_ids = list(object_ids)

    def _apply(self) -> bool:
        return self._storage.set_selection(self._object_ids)


class SelectOnlyShapeCommand(SetSelectionCommand):
    def __init__(self, storage: ShapeStorage, factory: AbstractFactory, shape: Shape) -> None:
        super().__init__(storage, factory, [shape.object_id()], "Выделить объект")


class ToggleShapeSelectionCommand(SnapshotCommand):
    def __init__(self, storage: ShapeStorage, factory: AbstractFactory, shape: Shape) -> None:
        super().__init__(storage, factory, "Переключить выделение")
        self._shape = shape

    def _apply(self) -> bool:
        return self._storage.toggle_selection(self._shape.object_id())


class SelectAllCommand(SnapshotCommand):
    def __init__(self, storage: ShapeStorage, factory: AbstractFactory) -> None:
        super().__init__(storage, factory, "Выделить все")

    def _apply(self) -> bool:
        return self._storage.select_all()


class ClearSelectionCommand(SnapshotCommand):
    def __init__(self, storage: ShapeStorage, factory: AbstractFactory) -> None:
        super().__init__(storage, factory, "Снять выделение")

    def _apply(self) -> bool:
        return self._storage.clear_selection()


class DeleteSelectedCommand(SnapshotCommand):
    def __init__(self, storage: ShapeStorage, factory: AbstractFactory) -> None:
        super().__init__(storage, factory, "Удалить выделенные объекты")

    def _apply(self) -> bool:
        return self._storage.remove_selected()


class GroupSelectedCommand(SnapshotCommand):
    def __init__(self, storage: ShapeStorage, factory: AbstractFactory) -> None:
        super().__init__(storage, factory, "Сгруппировать объекты")

    def _apply(self) -> bool:
        return self._storage.group_selected()


class UngroupSelectedCommand(SnapshotCommand):
    def __init__(self, storage: ShapeStorage, factory: AbstractFactory) -> None:
        super().__init__(storage, factory, "Разгруппировать объект")

    def _apply(self) -> bool:
        return self._storage.ungroup_selected()


class MoveSelectedCommand(SnapshotCommand):
    def __init__(
        self,
        storage: ShapeStorage,
        factory: AbstractFactory,
        dx: float,
        dy: float,
        bounds: QRectF,
        title: str = "Переместить выделенные объекты",
    ) -> None:
        super().__init__(storage, factory, title)
        self._dx = dx
        self._dy = dy
        self._bounds = QRectF(bounds)

    def _apply(self) -> bool:
        return self._storage.move_selected(self._dx, self._dy, self._bounds)


class ResizeSelectedCommand(SnapshotCommand):
    def __init__(self, storage: ShapeStorage, factory: AbstractFactory, delta: float, bounds: QRectF) -> None:
        super().__init__(storage, factory, "Изменить размер выделенных объектов")
        self._delta = delta
        self._bounds = QRectF(bounds)

    def _apply(self) -> bool:
        return self._storage.resize_selected(self._delta, self._bounds)


class RecolorSelectedCommand(SnapshotCommand):
    def __init__(self, storage: ShapeStorage, factory: AbstractFactory, color: QColor) -> None:
        super().__init__(storage, factory, "Изменить цвет выделенных объектов")
        self._color = QColor(color)

    def _apply(self) -> bool:
        return self._storage.recolor_selected(self._color)


class PasteObjectsCommand(SnapshotCommand):
    def __init__(
        self,
        storage: ShapeStorage,
        factory: AbstractFactory,
        objects_data: list[dict[str, Any]],
        bounds: QRectF,
        offset: float = 24.0,
    ) -> None:
        super().__init__(storage, factory, "Вставить объекты")
        self._objects_data = objects_data
        self._bounds = QRectF(bounds)
        self._offset = offset

    def _apply(self) -> bool:
        return self._storage.paste_objects(
            self._objects_data,
            self._factory,
            self._bounds,
            self._offset,
        )


class SetObjectPropertyCommand(SnapshotCommand):
    def __init__(
        self,
        storage: ShapeStorage,
        factory: AbstractFactory,
        object_id: str,
        property_name: str,
        property_value: Any,
        bounds: QRectF,
        property_label: str,
    ) -> None:
        super().__init__(storage, factory, f"Изменить свойство: {property_label}")
        self._object_id = object_id
        self._property_name = property_name
        self._property_value = property_value
        self._bounds = QRectF(bounds)

    def _apply(self) -> bool:
        return self._storage.apply_property_change(
            self._object_id,
            self._property_name,
            self._property_value,
            self._bounds,
        )


class LoadProjectCommand(SnapshotCommand):
    def __init__(
        self,
        storage: ShapeStorage,
        factory: AbstractFactory,
        file_path: str,
        bounds: QRectF,
    ) -> None:
        super().__init__(storage, factory, "Загрузить проект")
        self._file_path = file_path
        self._bounds = QRectF(bounds)

    def _apply(self) -> bool:
        self._storage.load_from_file(self._file_path, self._factory)
        self._storage.ensure_inside(self._bounds)
        return True
