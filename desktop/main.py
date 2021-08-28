from PyQt6.QtWidgets import QApplication
from GUI.main_app import TestChamberApp


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    test_chamber = TestChamberApp()
    test_chamber.show()
    sys.exit(app.exec())
