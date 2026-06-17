from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit,
                              QPushButton, QMessageBox)
import hashlib
from database.db import get_connection

class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Регистрация")
        self.resize(300, 200)
        v = QVBoxLayout()
        v.addWidget(QLabel("Логин:"))
        self.login = QLineEdit()
        v.addWidget(self.login)
        v.addWidget(QLabel("Пароль:"))
        self.p1 = QLineEdit()
        self.p1.setEchoMode(QLineEdit.Password)
        v.addWidget(self.p1)
        v.addWidget(QLabel("Повторите пароль:"))
        self.p2 = QLineEdit()
        self.p2.setEchoMode(QLineEdit.Password)
        v.addWidget(self.p2)
        btn = QPushButton("Зарегистрироваться")
        btn.clicked.connect(self.reg)
        v.addWidget(btn)
        self.setLayout(v)

    def reg(self):
        u = self.login.text().strip()
        p1 = self.p1.text().strip()
        p2 = self.p2.text().strip()
        if not u or not p1:
            QMessageBox.warning(self, "Ошибка", "Заполните поля")
            return
        if p1 != p2:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают")
            return
        if len(p1) < 4:
            QMessageBox.warning(self, "Ошибка", "Пароль минимум 4 символа")
            return
        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Нет связи с БД")
            return
        cur = conn.cursor()
        h = hashlib.sha256(p1.encode()).hexdigest()
        try:
            cur.execute("INSERT INTO users (username,password,role) VALUES (%s,%s,%s);",
                        (u, h, "user"))
            conn.commit()
            QMessageBox.information(self, "Успех", "Регистрация выполнена")
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            cur.close(); conn.close()
