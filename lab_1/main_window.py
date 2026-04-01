from PySide6.QtCore import QSize, Qt, QEvent, QTimer, Signal
from PySide6.QtGui import QMouseEvent, QPainter, QResizeEvent, QColor, QShortcut, QKeySequence
from PySide6.QtWidgets import (
    QPushButton,
    QVBoxLayout,
    QWidget,
    QStatusBar,
    QCheckBox,
    QTabWidget,
    QHBoxLayout,
    QLineEdit,
    QLabel,
    QFrame,
    QDial,
    QMainWindow,
    QDialog,
    QComboBox,
    QRadioButton,
    QProgressBar,
    QSlider,
    QSplitter,
)


class ButtonsWidget(QWidget):
    clicked = Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.buttons: list[QPushButton] = []

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            button = QPushButton(f"Кнопка {len(self.buttons) + 1}", self)
            button.clicked.connect(lambda _, b=button: b.setDisabled(True))
            button.move(event.position().toPoint())
            button.show()
            self.buttons.append(button)
            self.clicked.emit()
        super().mousePressEvent(event)

    def clear_buttons(self):
        for btn in self.buttons:
            btn.deleteLater()
        self.buttons.clear()

class MainWindow(QMainWindow):
    def eventFilter(self, obj, event):
        if obj == self.figure_frame and event.type() == QEvent.Type.Paint:
            self._paint_figure(event)
            return True
        return super().eventFilter(obj, event)

    def _paint_figure(self, event):
        painter = QPainter(self.figure_frame)
        color = self.selected_color
        qcolor = QColor(*color)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(qcolor)
        painter.setBrush(qcolor)
        width = self.figure_frame.width()
        height = self.figure_frame.height()
        size = self.selected_size
        x = width // 2
        y = height // 2
        if self.selected_figure == "circle":
            painter.drawEllipse(x - size // 2, y - size // 2, size, size)
        elif self.selected_figure == "square":
            painter.drawRect(x - size // 2, y - size // 2, size, size)
        elif self.selected_figure == "line":
            painter.setPen(qcolor)
            painter.drawLine(x - size // 2, y, x + size // 2, y)
        painter.end()

    @staticmethod
    def _mouse_button_to_text(button: Qt.MouseButton) -> str:
        if button == Qt.MouseButton.LeftButton:
            return "LeftButton"
        if button == Qt.MouseButton.RightButton:
            return "RightButton"
        if button == Qt.MouseButton.MiddleButton:
            return "MiddleButton"
        return str(button)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        button = event.button()
        pos = event.position().toPoint()
        self._update_status_bar(
            f"mousePressEvent: {self._mouse_button_to_text(button)} в точке {pos.toTuple()}"
        )
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        button = event.button()
        pos = event.position().toPoint()
        self._update_status_bar(
            f"mouseReleaseEvent: {self._mouse_button_to_text(button)} в точке {pos.toTuple()}"
        )
        super().mouseReleaseEvent(event)

    def resizeEvent(self, event: QResizeEvent) -> None:
        size = event.size()
        self._update_status_bar(f"Новый размер окна: {size.width()}x{size.height()}")
        super().resizeEvent(event)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__init_ui()

    def __init_ui(self):
        self.setMinimumSize(QSize(400, 400))
        self.setWindowTitle("Первая программа")

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        self.menu_bar = self.menuBar()

        self.selected_color = (0, 0, 0)
        self.available_figures = {"circle": "Круг", "square": "Квадрат", "line": "Линия"}
        self.selected_figure = "circle"
        self.selected_size = 50

        self.tabs: list[QWidget] = [QWidget() for _ in range(5)]

        self.__init_first_tab()
        self.__init_second_tab()
        self.__init_third_tab()
        self.__init_fourth_tab()
        self.__init_fifth_tab()
        self.__init_about_window()
        self.__init_menu_bar()

        self.info_text = QLabel("В этой программе много кнопок :)")

        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self.tabs[0], "Вкладка c кнопкой")
        self.tab_widget.addTab(self.tabs[1], "Вкладка диджея")
        self.tab_widget.addTab(self.tabs[2], "Пейнт")
        self.tab_widget.addTab(self.tabs[3], "Прогресс")
        self.tab_widget.addTab(self.tabs[4], "Хамстер Кликер")
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        layout.addWidget(self.info_text)
        layout.addWidget(self.tab_widget)

    def _change_paint_size(self, delta: int) -> None:
        new_value = self.selected_size + delta
        new_value = max(self.size_slider.minimum(), min(self.size_slider.maximum(), new_value))
        self.size_slider.setValue(new_value)
        self.selected_size = self.size_slider.value()
        self._update_status_bar(f"Размер фигуры изменён до {self.selected_size}")

    def __init_first_tab(self) -> None:
        """Инициализация вкладки с кнопками"""
        tab = self.tabs[0]
        layout = QVBoxLayout(tab)

        self.main_button = QPushButton("Я самая главная кнопка!")
        self.check_box = QCheckBox("Видна ли кнопка?")
        self.button_info = QLabel("Информация о кнопке: Ничего особенного...")

        self.check_box.setChecked(True)
        self.check_box.stateChanged.connect(self.__hide_main_button)

        self.main_button.clicked.connect(self.__clicked_main_button)
        self.main_button.pressed.connect(self.__pressed_main_button)
        self.main_button.released.connect(
            lambda: self._update_status_bar("Главная кнопка отпущена")
        )

        button_text_change_widget = QWidget()
        text_change_layout = QHBoxLayout()

        self.button_text_edit = QLineEdit()
        self.button_text_edit.setPlaceholderText("Введите новое название кнопки")
        self.button_text_edit.textChanged.connect(
            lambda text: self._update_status_bar(
                f"Текст для кнопки введён: {repr(text)}"
            )
        )

        self.button_text_confirm = QPushButton("Поменять")
        self.button_text_confirm.clicked.connect(self.__change_button_text)

        text_change_layout.addWidget(self.button_text_edit)
        text_change_layout.addWidget(self.button_text_confirm)

        button_text_change_widget.setLayout(text_change_layout)

        layout.addWidget(button_text_change_widget)
        layout.addWidget(self.check_box)
        layout.addWidget(self.button_info)
        layout.addWidget(self.main_button)

    def __init_second_tab(self) -> None:
        """Инициализация второй вкладки"""
        tab = self.tabs[1]

        layout = QVBoxLayout(tab)
        dj_label = QLabel("Добро пожаловать на вкладку диджея!")

        dj_table = QFrame()
        dj_table.setFrameShape(QFrame.Shape.Panel)
        dj_table_layout = QHBoxLayout(dj_table)

        tracks_containers: list[tuple] = []

        for i in range(1, 6):
            track_widget = QWidget()
            track_layout = QVBoxLayout(track_widget)

            level = QLabel("50")
            dial = QDial()
            btn = QPushButton(f"Трек {i}")

            tracks_containers.append((level, dial, btn))

            btn.clicked.connect(
                lambda _, x=i: self._update_status_bar(f"Воспроизведение трека {x}")
            )

            dial.setNotchesVisible(True)
            dial.setValue(50)

            def change_volume(x):
                value = str(tracks_containers[x - 1][1].value())
                self._update_status_bar(f"Установка громкости трека {x} на {value}")
                tracks_containers[x - 1][0].setText(value)

            dial.valueChanged.connect(lambda _, x=i: change_volume(x))

            for x in range(3):
                track_layout.addWidget(
                    tracks_containers[i - 1][x], alignment=Qt.AlignmentFlag.AlignHCenter
                )

            dj_table_layout.addWidget(track_widget)

        layout.addWidget(dj_label)
        layout.addWidget(dj_table)

    def __init_third_tab(self) -> None:
        tab = self.tabs[2]
        tab_layout = QHBoxLayout(tab)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        tab_layout.addWidget(splitter)
        control_widget = QWidget()
        control_layout = QVBoxLayout(control_widget)

        self.figure_frame = QFrame()
        self.figure_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.figure_frame.installEventFilter(self)

        # Цвет
        color_widget = QWidget()
        color_layout = QHBoxLayout(color_widget)
        self.available_colors = {
            "Чёрный": (0, 0, 0),
            "Красный": (255, 0, 0),
            "Зелёный": (0, 255, 0),
            "Синий": (0, 0, 255),
            "Белый": (255, 255, 255),
        }
        self.colors_combobox = QComboBox()
        self.colors_combobox.addItems(list(self.available_colors))
        color_layout.addWidget(QLabel("Введите цвет"))
        color_layout.addWidget(self.colors_combobox)
        self.colors_combobox.currentTextChanged.connect(self._on_color_changed)

        # Фигура
        figure_select_widget = QWidget()
        figure_select_layout = QHBoxLayout(figure_select_widget)
        figure_select_layout.addWidget(QLabel("Укажите фигуру"))
        self.figure_radio_buttons = []
        self.figure_radio_names = ["circle", "square", "line"]
        for name, label in self.available_figures.items():
            btn = QRadioButton(label)
            btn.toggled.connect(lambda checked, n=name: self._on_figure_changed(n, checked))
            self.figure_radio_buttons.append(btn)
            figure_select_layout.addWidget(btn)
        self.figure_radio_buttons[0].setChecked(True)

        # Размер
        size_widget = QWidget()
        size_layout = QHBoxLayout(size_widget)
        size_layout.addWidget(QLabel("Введите размер фигуры"))
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setMinimum(10)
        self.size_slider.setMaximum(200)
        self.size_slider.setValue(self.selected_size)
        self.size_slider.valueChanged.connect(self._on_size_changed)
        size_layout.addWidget(self.size_slider)

        control_layout.addWidget(color_widget)
        control_layout.addWidget(figure_select_widget)
        control_layout.addWidget(size_widget)

        splitter.addWidget(control_widget)
        splitter.addWidget(self.figure_frame)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 3)

        # Горячие клавиши изменения размера (+ / -)
        for seq, delta in (
            ("+", +5),
            ("=", +5),
            ("-", -5),
            ("_", -5),
        ):
            shortcut = QShortcut(QKeySequence(seq), tab)
            shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
            shortcut.activated.connect(lambda d=delta: self._change_paint_size(d))

        for w in [
            control_widget,
            self.colors_combobox,
            self.size_slider,
            self.figure_frame,
            *self.figure_radio_buttons,
        ]:
            try:
                w.installEventFilter(tab)
            except Exception:
                pass

    def __init_fourth_tab(self) -> None:
        tab = self.tabs[3]
        layout = QVBoxLayout(tab)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(QLabel("Прогресс по таймеру"))
        layout.addWidget(self.progress_bar)

        self.progress_timer = QTimer(self)
        self.progress_timer.setInterval(100)
        self.progress_timer.timeout.connect(self._on_progress_tick)
        self.progress_timer.start()

    def __init_fifth_tab(self) -> None:
        tab = self.tabs[4]
        layout = QVBoxLayout(tab)

        self.clear_button = QPushButton("Очистить от кнопок")
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        self.buttons_widget = ButtonsWidget()

        self.clear_button.clicked.connect(self.buttons_widget.clear_buttons)

        layout.addWidget(
            self.clear_button,
            alignment=Qt.AlignmentFlag.AlignCenter,
        )
        frame_layout.addWidget(self.buttons_widget)
        layout.addWidget(frame)


    def _on_progress_tick(self) -> None:
        value = self.progress_bar.value() + 1
        if value > 100:
            value = 0
        self.progress_bar.setValue(value)

    def _on_color_changed(self, color_name: str) -> None:
        self.selected_color = self.available_colors[color_name]
        self.figure_frame.update()

    def _on_figure_changed(self, figure_name: str, checked: bool) -> None:
        if checked:
            self.selected_figure = figure_name
            self.figure_frame.update()

    def _on_size_changed(self, value: int) -> None:
        self.selected_size = value
        self.figure_frame.update()

    def __init_about_window(self) -> None:
        self.about_window = QDialog()
        self.about_window.setWindowTitle("О программе")
        about_layout = QVBoxLayout(self.about_window)
        about_label = QLabel(
            "Это программа для первой лабораторной на PySide6.\nАвтор: Давлетов Артур. 2026 г."
        )
        ok_button = QPushButton("ОК")
        ok_button.clicked.connect(self.about_window.close)
        about_layout.addWidget(about_label)
        about_layout.addWidget(
            ok_button,
            alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom,
        )

    def __init_menu_bar(self) -> None:
        file_menu = self.menu_bar.addMenu("Файл")
        file_menu.addAction("Выход", self.close)
        help_menu = self.menu_bar.addMenu("Помощь")
        help_menu.addAction("О программе", self.about_window.show)

    def __hide_main_button(self, state: int) -> None:
        self._update_status_bar(f"Чекбокс изменён: {state}")
        if state == 0:
            self.main_button.hide()
            self.button_info.setText("Информация о кнопке: Кнопка скрыта.")
        else:
            self.main_button.show()
            self.button_info.setText("Информация о кнопке: Ничего особенного...")

    def __change_button_text(self) -> None:
        text = self.button_text_edit.text()
        self.main_button.setText(text)
        self._update_status_bar(f"Текст главной кнопки изменён: {repr(text)}")

    def __clicked_main_button(self) -> None:
        self.button_info.setText("Информация о кнопке: Ничего особенного...")
        self._update_status_bar("Главная кнопка нажата")

    def __pressed_main_button(self) -> None:
        self.button_info.setText("Информация о кнопке: Кнопка удерживается.")
        self._update_status_bar("Главная кнопка удерживается")

    def _update_status_bar(self, message: str, timeout: int = 5000) -> None:
        """Обновляет статус бар сообщением на определённое время"""
        self.status_bar.showMessage(message, timeout)


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)

    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec())
