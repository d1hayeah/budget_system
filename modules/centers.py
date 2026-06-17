from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QTableWidget, QTableWidgetItem, QPushButton,
                              QLineEdit, QMessageBox, QHeaderView)
from PyQt5.QtGui import QColor, QBrush
from database.db import get_connection

class CentersWindow(QWidget):
    def __init__(self, role):
        super().__init__()
        self.role = role
        self.sel_id = None
        self.setWindowTitle("Центры ответственности")
        self.resize(700, 400)
        v = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Название", "Ответственный", "Цвет"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.cellClicked.connect(self.on_click)
        v.addWidget(self.table)

        h = QHBoxLayout()
        h.addWidget(QLabel("Название:"))
        self.name = QLineEdit()
        h.addWidget(self.name)
        h.addWidget(QLabel("Ответственный:"))
        self.resp = QLineEdit()
        h.addWidget(self.resp)
        v.addLayout(h)

        h2 = QHBoxLayout()
        self.btn_add = QPushButton("Добавить")
        self.btn_add.clicked.connect(self.add)
        h2.addWidget(self.btn_add)
        self.btn_upd = QPushButton("Изменить")
        self.btn_upd.clicked.connect(self.update)
        h2.addWidget(self.btn_upd)
        self.btn_del = QPushButton("Удалить")
        self.btn_del.clicked.connect(self.delete)
        h2.addWidget(self.btn_del)
        v.addLayout(h2)

        if self.role != "admin":
            self.btn_add.setEnabled(False)
            self.btn_upd.setEnabled(False)
            self.btn_del.setEnabled(False)

        self.setLayout(v)
        self.load()

    def load(self):
        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Нет связи с БД")
            return
        cur = conn.cursor()
        cur.execute("SELECT id, name, responsible, color FROM centers ORDER BY name;")
        rows = cur.fetchall()
        self.table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(str(r[0])))
            self.table.setItem(i, 1, QTableWidgetItem(r[1]))
            self.table.setItem(i, 2, QTableWidgetItem(r[2] or ""))
            it = QTableWidgetItem(r[3] or "")
            if r[3]:
                it.setBackground(QBrush(QColor(r[3])))
            self.table.setItem(i, 3, it)
        cur.close(); conn.close()

    def on_click(self, row, col):
        self.sel_id = self.table.item(row, 0).text()
        self.name.setText(self.table.item(row, 1).text())
        self.resp.setText(self.table.item(row, 2).text())

    def add(self):
        if self.role != "admin": return
        n = self.name.text().strip()
        if not n:
            QMessageBox.warning(self, "Ошибка", "Введите название")
            return
        conn = get_connection()
        if not conn: return
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO centers (name, responsible) VALUES (%s,%s);",
                        (n, self.resp.text()))
            conn.commit()
            self.load()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            cur.close(); conn.close()

    def update(self):
        if self.role != "admin" or not self.sel_id: return
        conn = get_connection()
        if not conn: return
        cur = conn.cursor()
        try:
            cur.execute("UPDATE centers SET name=%s, responsible=%s WHERE id=%s;",
                        (self.name.text(), self.resp.text(), self.sel_id))
            conn.commit()
            self.load()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            cur.close(); conn.close()

    def delete(self):
        if self.role != "admin" or not self.sel_id: return
        if QMessageBox.question(self, "?", "Удалить?") != QMessageBox.Yes:
            return
        conn = get_connection()
        if not conn: return
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM centers WHERE id=%s;", (self.sel_id,))
            conn.commit()
            self.sel_id = None
            self.load()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            cur.close(); conn.close()
