from abc import ABC, abstractmethod

from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QColor

from shape_storage import AbstractFactory, ShapeStorage
from shapes import Shape


class Command(ABC):
    @abstractmethod
    def execute(self) -> bool:
        pass

    @abstractmethod
    def undo(self) -> None:
        pass


class CommandStack:
    def __init__(self) -> None:
        self._undo_stack: list[Command] = []

    def execute(self, command: Command) -> bool:
        if not command.execute():
            return False
        self._undo_stack.append(command)
        return True

    def push_committed(self, command: Command) -> bool:
        if not command.execute():
            return False
        self._undo_stack.append(command)
        return True

    def undo(self) -> bool:
        if not self._undo_stack:
            return False
        command = self._undo_stack.pop()
        command.undo()
        return True

    def can_undo(self) -> bool:
        return bool(self._undo_stack)


class SnapshotCommand(Command):
    def __init__(self, storage: ShapeStorage, factory: AbstractFactory) -> None:
        self._storage = storage
        self._factory = factory
        self._before: list[dict] = []

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
        before: list[dict],
        after: list[dict],
    ) -> None:
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
        super().__init__(storage, factory)
        self._shape_type = shape_type
        self._point = QPointF(point)
        self._bounds = QRectF(bounds)
        self._keep_selection = keep_selection

    def _apply(self) -> bool:
        shape = self._factory.create_at(self._shape_type, self._point, self._bounds)
        if not self._keep_selection:
            self._storage.clear_selection()
        shape.set_selected(True)
        self._storage.add(shape)
        return True


class SelectOnlyShapeCommand(SnapshotCommand):
    def __init__(self, storage: ShapeStorage, factory: AbstractFactory, shape: Shape) -> None:
        super().__init__(storage, factory)
        self._shape = shape

    def _apply(self) -> bool:
        self._storage.clear_selection()
        self._shape.set_selected(True)
        return True


class ToggleShapeSelectionCommand(SnapshotCommand):
    def __init__(self, storage: ShapeStorage, factory: AbstractFactory, shape: Shape) -> None:
        super().__init__(storage, factory)
        self._shape = shape

    def _apply(self) -> bool:
        self._shape.set_selected(not self._shape.is_selected())
        return True


class SelectAllCommand(SnapshotCommand):
    def _apply(self) -> bool:
        self._storage.select_all()
        return True


class ClearSelectionCommand(SnapshotCommand):
    def _apply(self) -> bool:
        self._storage.clear_selection()
        return True


class DeleteSelectedCommand(SnapshotCommand):
    def _apply(self) -> bool:
        if self._storage.selected_count() == 0:
            return False
        self._storage.remove_selected()
        return True


class GroupSelectedCommand(SnapshotCommand):
    def _apply(self) -> bool:
        return self._storage.group_selected()


class UngroupSelectedCommand(SnapshotCommand):
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
    ) -> None:
        super().__init__(storage, factory)
        self._dx = dx
        self._dy = dy
        self._bounds = QRectF(bounds)

    def _apply(self) -> bool:
        if self._storage.selected_count() == 0:
            return False
        self._storage.move_selected(self._dx, self._dy, self._bounds)
        return True


class ResizeSelectedCommand(SnapshotCommand):
    def __init__(self, storage: ShapeStorage, factory: AbstractFactory, delta: float, bounds: QRectF) -> None:
        super().__init__(storage, factory)
        self._delta = delta
        self._bounds = QRectF(bounds)

    def _apply(self) -> bool:
        if self._storage.selected_count() == 0:
            return False
        self._storage.resize_selected(self._delta, self._bounds)
        return True


class RecolorSelectedCommand(SnapshotCommand):
    def __init__(self, storage: ShapeStorage, factory: AbstractFactory, color: QColor) -> None:
        super().__init__(storage, factory)
        self._color = QColor(color)

    def _apply(self) -> bool:
        if self._storage.selected_count() == 0:
            return False
        self._storage.recolor_selected(self._color)
        return True


class LoadProjectCommand(SnapshotCommand):
    def __init__(
        self,
        storage: ShapeStorage,
        factory: AbstractFactory,
        file_path: str,
        bounds: QRectF,
    ) -> None:
        super().__init__(storage, factory)
        self._file_path = file_path
        self._bounds = QRectF(bounds)

    def _apply(self) -> bool:
        self._storage.load_from_file(self._file_path, self._factory)
        self._storage.ensure_inside(self._bounds)
        return True
