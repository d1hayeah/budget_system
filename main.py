import sys
from PyQt5.QtWidgets import QApplication
from database.db import ensure_tables
from auth.login import LoginWindow

if __name__ == "__main__":
    ensure_tables()
    app = QApplication(sys.argv)
    app.setApplicationName("Система Бюджетирования")
    w = LoginWindow()
    w.show()
    sys.exit(app.exec_())
