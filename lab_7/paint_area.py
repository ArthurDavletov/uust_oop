from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QKeyEvent, QMouseEvent, QPaintEvent, QPainter, QPen, QResizeEvent
from PySide6.QtWidgets import QWidget

from commands import (
    ClearSelectionCommand,
    Command,
    CommandStack,
    CommittedSnapshotCommand,
    CreateArrowCommand,
    CreateShapeCommand,
    DeleteSelectedCommand,
    GroupSelectedCommand,
    LoadProjectCommand,
    MoveSelectedCommand,
    RecolorSelectedCommand,
    ResizeSelectedCommand,
    SelectAllCommand,
    SelectOnlyShapeCommand,
    ToggleShapeSelectionCommand,
    UngroupSelectedCommand,
)
from shape_storage import ShapeStorage
from shapes import Shape, ShapeFactory


class PaintArea(QWidget):
    selectionChanged = Signal(bool)
    undoAvailabilityChanged = Signal(bool)
    arrowModeChanged = Signal(bool, str)
    MOVE_STEP = 10
    FAST_MOVE_STEP = 20
    SCALE_STEP = 10
    WORKSPACE_MARGIN = 12.0

    def __init__(self, storage: ShapeStorage, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._storage = storage
        self._storage.add_observer(self)
        self._shape_factory = ShapeFactory.default()
        self._command_stack = CommandStack()
        self._current_shape = "circle"
        self._drag_start_snapshot: list[dict] | None = None
        self._drag_last_pos: QPointF | None = None
        self._drag_moved = False
        self._arrow_mode = False
        self._arrow_source: Shape | None = None
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMinimumSize(640, 420)

    def storage_changed(self, storage: ShapeStorage, reason: str) -> None:
        del storage, reason
        self.update()
        self.selectionChanged.emit(self.has_selection())

    def set_shape_type(self, shape_type: str) -> None:
        self._current_shape = shape_type
        self.setFocus()

    def has_selection(self) -> bool:
        return self._storage.selected_count() > 0

    def can_group_selection(self) -> bool:
        return self._storage.groupable_selected_count() >= 2

    def can_ungroup_selection(self) -> bool:
        return self._storage.has_selected_group()

    def can_undo(self) -> bool:
        return self._command_stack.can_undo()

    def is_arrow_mode_active(self) -> bool:
        return self._arrow_mode

    def start_arrow_creation(self) -> None:
        self._arrow_mode = True
        self._arrow_source = None
        self.arrowModeChanged.emit(True, "Выберите объект-источник стрелки")
        self.setFocus()

    def cancel_arrow_creation(self) -> None:
        if not self._arrow_mode and self._arrow_source is None:
            return
        self._arrow_mode = False
        self._arrow_source = None
        self.arrowModeChanged.emit(False, "")

    def undo(self) -> None:
        self.cancel_arrow_creation()
        if self._command_stack.undo():
            self._finish_change()
            self._emit_undo_state()

    def delete_selected(self) -> None:
        self.cancel_arrow_creation()
        self._run_command(DeleteSelectedCommand(self._storage, self._shape_factory))

    def clear_selection(self) -> None:
        self.cancel_arrow_creation()
        self._run_command(ClearSelectionCommand(self._storage, self._shape_factory))

    def select_all(self) -> None:
        self.cancel_arrow_creation()
        self._run_command(SelectAllCommand(self._storage, self._shape_factory))

    def group_selected(self) -> None:
        self.cancel_arrow_creation()
        self._run_command(GroupSelectedCommand(self._storage, self._shape_factory))

    def ungroup_selected(self) -> None:
        self.cancel_arrow_creation()
        self._run_command(UngroupSelectedCommand(self._storage, self._shape_factory))

    def recolor_selected(self, color: QColor) -> None:
        self._run_command(RecolorSelectedCommand(self._storage, self._shape_factory, color))

    def save_to_file(self, file_path: str) -> None:
        self._storage.save_to_file(file_path)

    def load_from_file(self, file_path: str) -> None:
        self.cancel_arrow_creation()
        self._run_command(LoadProjectCommand(self._storage, self._shape_factory, file_path, self._workspace_rect()))

    def paintEvent(self, event: QPaintEvent) -> None:
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor("#dfe6e9"))
        painter.fillRect(self._workspace_rect(), QColor("#ffffff"))
        painter.setPen(QPen(QColor("#95a5a6"), 2))
        painter.drawRect(self._workspace_rect())

        for shape in self._storage.iter_draw_order():
            shape.draw(painter)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() != Qt.LeftButton:
            return

        self.setFocus()
        point = event.position()
        if not self._workspace_rect().contains(point):
            return

        if self._arrow_mode:
            self._handle_arrow_click(point)
            event.accept()
            return

        ctrl_pressed = bool(event.modifiers() & Qt.ControlModifier)
        shape = self._storage.shape_at(point)

        if shape is None:
            self._run_command(
                CreateShapeCommand(
                    self._storage,
                    self._shape_factory,
                    self._current_shape,
                    point,
                    self._workspace_rect(),
                    ctrl_pressed,
                )
            )
            return

        if ctrl_pressed:
            self._run_command(ToggleShapeSelectionCommand(self._storage, self._shape_factory, shape))
            return

        if not shape.is_selected():
            self._run_command(SelectOnlyShapeCommand(self._storage, self._shape_factory, shape))

        self._begin_drag(point)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._drag_last_pos is None or not (event.buttons() & Qt.LeftButton):
            super().mouseMoveEvent(event)
            return

        point = event.position()
        dx = point.x() - self._drag_last_pos.x()
        dy = point.y() - self._drag_last_pos.y()
        if dx == 0 and dy == 0:
            return

        self._storage.move_selected(dx, dy, self._workspace_rect())
        self._drag_last_pos = point
        self._drag_moved = True
        self._finish_change()
        event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() != Qt.LeftButton or self._drag_start_snapshot is None:
            super().mouseReleaseEvent(event)
            return

        if self._drag_moved:
            after = self._storage.snapshot()
            self._command_stack.push_committed(
                CommittedSnapshotCommand(
                    self._storage,
                    self._shape_factory,
                    self._drag_start_snapshot,
                    after,
                )
            )
            self._finish_change()
            self._emit_undo_state()

        self._reset_drag()
        event.accept()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Escape and self._arrow_mode:
            self.cancel_arrow_creation()
            event.accept()
            return

        step = self.MOVE_STEP
        if event.modifiers() & Qt.ShiftModifier:
            step = self.FAST_MOVE_STEP

        bounds = self._workspace_rect()

        match event.key():
            case Qt.Key_A if event.modifiers() & Qt.ControlModifier:
                self.select_all()
                event.accept()
            case Qt.Key_G if event.modifiers() & Qt.ControlModifier:
                self.group_selected()
                event.accept()
            case Qt.Key_U if event.modifiers() & Qt.ControlModifier:
                self.ungroup_selected()
                event.accept()
            case Qt.Key_Z if event.modifiers() & Qt.ControlModifier:
                self.undo()
                event.accept()
            case Qt.Key_Delete:
                self.delete_selected()
                event.accept()
            case Qt.Key_Escape:
                self.clear_selection()
                event.accept()
            case Qt.Key_Left:
                self._run_command(MoveSelectedCommand(self._storage, self._shape_factory, -step, 0, bounds))
                event.accept()
            case Qt.Key_Right:
                self._run_command(MoveSelectedCommand(self._storage, self._shape_factory, step, 0, bounds))
                event.accept()
            case Qt.Key_Up:
                self._run_command(MoveSelectedCommand(self._storage, self._shape_factory, 0, -step, bounds))
                event.accept()
            case Qt.Key_Down:
                self._run_command(MoveSelectedCommand(self._storage, self._shape_factory, 0, step, bounds))
                event.accept()
            case Qt.Key_Plus | Qt.Key_Equal:
                self._run_command(ResizeSelectedCommand(self._storage, self._shape_factory, self.SCALE_STEP, bounds))
                event.accept()
            case Qt.Key_Minus:
                self._run_command(ResizeSelectedCommand(self._storage, self._shape_factory, -self.SCALE_STEP, bounds))
                event.accept()
            case _:
                super().keyPressEvent(event)

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self._storage.ensure_inside(self._workspace_rect())
        self._finish_change()

    def _handle_arrow_click(self, point: QPointF) -> None:
        shape = self._storage.shape_at(point)
        if shape is None or not shape.can_create_links():
            return

        if self._arrow_source is None:
            self._arrow_source = shape
            self._storage.select_only(shape.object_id())
            self.arrowModeChanged.emit(True, f"Источник: {shape.display_name()}. Выберите объект-приемник")
            return

        if shape.object_id() == self._arrow_source.object_id():
            self.arrowModeChanged.emit(True, "Источник и приемник стрелки должны различаться")
            return

        created = self._run_command(CreateArrowCommand(self._storage, self._shape_factory, self._arrow_source, shape))
        if created:
            self.cancel_arrow_creation()
        else:
            self.arrowModeChanged.emit(True, "Такую стрелку создать нельзя или она уже существует")

    def _begin_drag(self, point: QPointF) -> None:
        self._drag_start_snapshot = self._storage.snapshot()
        self._drag_last_pos = QPointF(point)
        self._drag_moved = False

    def _reset_drag(self) -> None:
        self._drag_start_snapshot = None
        self._drag_last_pos = None
        self._drag_moved = False

    def _run_command(self, command: Command) -> bool:
        if self._command_stack.execute(command):
            self._finish_change()
            self._emit_undo_state()
            return True
        return False

    def _workspace_rect(self) -> QRectF:
        margin = self.WORKSPACE_MARGIN
        return QRectF(self.rect()).adjusted(margin, margin, -margin, -margin)

    def _finish_change(self) -> None:
        self.update()
        self.selectionChanged.emit(self.has_selection())

    def _emit_undo_state(self) -> None:
        self.undoAvailabilityChanged.emit(self.can_undo())
