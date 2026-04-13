from PySide6.QtWidgets import QMainWindow, QApplication
import sys

class CCircle:
    def __init__(self, x: int, y: int, r: int):
        self.x = x
        self.y = y
        self.r = r

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs) -> None:
        super(*args, **kwargs).__init__()
        self.setWindowTitle("Круги на форме")
        self.setMinimumSize(400, 400)
        self.__post_init__()

    def __post_init__(self) -> None:
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())