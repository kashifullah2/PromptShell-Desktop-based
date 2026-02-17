import sys
from PySide6.QtWidgets import QApplication
from src.ui.main_window import PromptShellWindow

def main():
    app = QApplication(sys.argv)
    window = PromptShellWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()