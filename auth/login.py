from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit,
                              QPushButton, QMessageBox)
import hashlib
from database.db import get_connection

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Авторизация")
        self.resize(300, 180)
        v = QVBoxLayout()
        v.addWidget(QLabel("Логин:"))
        self.login = QLineEdit()
        v.addWidget(self.login)
        v.addWidget(QLabel("Пароль:"))
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        v.addWidget(self.password)
        self.btn_ok = QPushButton("Войти")
        self.btn_ok.clicked.connect(self.check)
        v.addWidget(self.btn_ok)
        self.btn_reg = QPushButton("Регистрация")
        self.btn_reg.clicked.connect(self.open_reg)
        v.addWidget(self.btn_reg)
        self.setLayout(v)

    def check(self):
        u = self.login.text().strip()
        p = self.password.text().strip()
        if not u or not p:
            QMessageBox.warning(self, "Ошибка", "Введите логин и пароль")
            return
        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Нет связи с БД")
            return
        cur = conn.cursor()
        h = hashlib.sha256(p.encode()).hexdigest()
        cur.execute("SELECT id, username, role FROM users WHERE username=%s AND password=%s;",
                    (u, h))
        row = cur.fetchone()
        cur.close(); conn.close()
        if row:
            from modules.menu import MenuWindow
            self.hide()
            self.m = MenuWindow(row[1], row[2], row[0])
            self.m.show()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")

    def open_reg(self):
        from auth.register import RegisterWindow
        self.r = RegisterWindow()
        self.r.show()
