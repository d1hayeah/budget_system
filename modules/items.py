from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QTableWidget, QTableWidgetItem, QPushButton,
                              QLineEdit, QComboBox, QMessageBox, QHeaderView)
from database.db import get_connection

class ItemsWindow(QWidget):
    def __init__(self, role):
        super().__init__()
        self.role = role
        self.sel_id = None
        self.setWindowTitle("Статьи бюджета")
        self.resize(600, 400)
        v = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Код", "Название", "Тип"])
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.cellClicked.connect(self.on_click)
        v.addWidget(self.table)

        h = QHBoxLayout()
        h.addWidget(QLabel("Код:"))
        self.code = QLineEdit()
        h.addWidget(self.code)
        h.addWidget(QLabel("Название:"))
        self.name = QLineEdit()
        h.addWidget(self.name)
        h.addWidget(QLabel("Тип:"))
        self.type = QComboBox()
        self.type.addItems(["Доход", "Расход"])
        h.addWidget(self.type)
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
        cur.execute("SELECT id, code, name, item_type FROM items ORDER BY code;")
        rows = cur.fetchall()
        self.table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            for j in range(4):
                self.table.setItem(i, j, QTableWidgetItem(str(r[j])))
        cur.close(); conn.close()

    def on_click(self, row, col):
        self.sel_id = self.table.item(row, 0).text()
        self.code.setText(self.table.item(row, 1).text())
        self.name.setText(self.table.item(row, 2).text())
        self.type.setCurrentText(self.table.item(row, 3).text())

    def add(self):
        if self.role != "admin": return
        conn = get_connection()
        if not conn: return
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO items (code,name,item_type) VALUES (%s,%s,%s);",
                        (self.code.text(), self.name.text(), self.type.currentText()))
            conn.commit(); self.load()
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
            cur.execute("UPDATE items SET code=%s,name=%s,item_type=%s WHERE id=%s;",
                        (self.code.text(), self.name.text(), self.type.currentText(), self.sel_id))
            conn.commit(); self.load()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            cur.close(); conn.close()

    def delete(self):
        if self.role != "admin" or not self.sel_id: return
        if QMessageBox.question(self, "?", "Удалить?") != QMessageBox.Yes: return
        conn = get_connection()
        if not conn: return
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM items WHERE id=%s;", (self.sel_id,))
            conn.commit(); self.sel_id = None; self.load()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            cur.close(); conn.close()
