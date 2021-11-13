from sys import argv, exit

from PyQt6.QtWidgets import QApplication

from app import App


if __name__ == '__main__':
    qt_app = QApplication(argv)
    main_app = App()
    exit(qt_app.exec())
