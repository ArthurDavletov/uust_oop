from __future__ import annotations

from PySide6.QtCore import QSignalBlocker, Qt, Signal
from PySide6.QtWidgets import QAbstractItemView, QTreeWidget, QTreeWidgetItem

from shape_storage import ShapeStorage
from shapes import Shape


class StorageTreeView(QTreeWidget):
    selectionRequested = Signal(list)

    def __init__(self, storage: ShapeStorage, parent=None) -> None:
        super().__init__(parent)
        self._storage = storage
        self._storage.add_observer(self)

        self.setColumnCount(2)
        self.setHeaderLabels(["Объект", "Связь"])
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setAlternatingRowColors(True)
        self.setRootIsDecorated(True)
        self.itemSelectionChanged.connect(self._apply_tree_selection)

        self.rebuild()

    def storage_changed(self, storage: ShapeStorage, reason: str) -> None:
        del storage, reason
        self.rebuild()

    def rebuild(self) -> None:
        expanded_ids = self._expanded_ids()
        selected_ids = {shape.object_id() for shape in self._storage.selected_shapes()}

        blocker = QSignalBlocker(self)
        self.clear()
        for shape in self._storage.top_level_shapes():
            self._append_item(None, shape, expanded_ids, selected_ids)
        del blocker

        for column in range(self.columnCount()):
            self.resizeColumnToContents(column)

    def _append_item(
        self,
        parent_item: QTreeWidgetItem | None,
        shape: Shape,
        expanded_ids: set[str],
        selected_ids: set[str],
    ) -> None:
        item = QTreeWidgetItem([shape.display_name(), shape.details_text()])
        item.setData(0, Qt.UserRole, shape.object_id())
        item.setData(0, Qt.UserRole + 1, True)

        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

        if parent_item is None:
            self.addTopLevelItem(item)
        else:
            parent_item.addChild(item)

        item.setExpanded(shape.object_id() in expanded_ids)
        if shape.object_id() in selected_ids:
            item.setSelected(True)

        for child in shape.children():
            self._append_item(item, child, expanded_ids, selected_ids)

    def _apply_tree_selection(self) -> None:
        selected_ids: list[str] = []
        for item in self.selectedItems():
            if not item.data(0, Qt.UserRole + 1):
                continue
            object_id = item.data(0, Qt.UserRole)
            if isinstance(object_id, str):
                selected_ids.append(object_id)
        self.selectionRequested.emit(selected_ids)

    def _expanded_ids(self) -> set[str]:
        expanded_ids: set[str] = set()

        def walk(item: QTreeWidgetItem) -> None:
            object_id = item.data(0, Qt.UserRole)
            if item.isExpanded() and isinstance(object_id, str):
                expanded_ids.add(object_id)
            for index in range(item.childCount()):
                walk(item.child(index))

        for index in range(self.topLevelItemCount()):
            walk(self.topLevelItem(index))
        return expanded_ids
