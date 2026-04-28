from __future__ import annotations

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QAbstractItemView, QListWidget, QListWidgetItem

from commands import CommandStack


class CommandHistoryView(QListWidget):
    def __init__(self, command_stack: CommandStack, parent=None) -> None:
        super().__init__(parent)
        self._command_stack = command_stack
        self._command_stack.add_observer(self)
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.refresh()

    def history_changed(self, stack: CommandStack) -> None:
        del stack
        self.refresh()

    def refresh(self) -> None:
        self.clear()
        entries = self._command_stack.history_entries()
        if not entries:
            item = QListWidgetItem("История команд пока пуста")
            item.setForeground(QColor("#7f8c8d"))
            self.addItem(item)
            return

        for entry in entries:
            prefix = "[x]" if entry.is_done else "[ ]"
            item = QListWidgetItem(f"{prefix} {entry.title}")
            if not entry.is_done:
                item.setForeground(QColor("#7f8c8d"))
            elif entry.is_current:
                item.setForeground(QColor("#1e8449"))
            self.addItem(item)
        self.scrollToBottom()
