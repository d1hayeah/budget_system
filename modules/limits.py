from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QTableWidget, QTableWidgetItem, QPushButton,
                              QComboBox, QDateEdit, QDoubleSpinBox, QMessageBox, QHeaderView)
from PyQt5.QtCore import QDate
from database.db import get_connection

class LimitsWindow(QWidget):
    def __init__(self, role):
        super().__init__()
        self.role = role
        self.sel_id = None
        self.setWindowTitle("Лимиты и контроль")
        self.resize(800, 450)
        v = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID","Центр","Статья","Лимит","Использовано","Статус"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.cellClicked.connect(self.on_click)
        v.addWidget(self.table)

        h = QHBoxLayout()
        h.addWidget(QLabel("Центр:"))
        self.center = QComboBox()
        h.addWidget(self.center)
        h.addWidget(QLabel("Статья:"))
        self.item = QComboBox()
        h.addWidget(self.item)
        h.addWidget(QLabel("Период:"))
        self.period = QDateEdit()
        self.period.setCalendarPopup(True)
        self.period.setDisplayFormat("yyyy-MM")
        self.period.setDate(QDate.currentDate().addDays(-7))
        h.addWidget(self.period)
        h.addWidget(QLabel("Лимит:"))
        self.limit = QDoubleSpinBox()
        self.limit.setMaximum(99999999)
        h.addWidget(self.limit)
        v.addLayout(h)

        h2 = QHBoxLayout()
        self.btn_add = QPushButton("Установить")
        self.btn_add.clicked.connect(self.add)
        h2.addWidget(self.btn_add)
        self.btn_del = QPushButton("Удалить")
        self.btn_del.clicked.connect(self.delete)
        h2.addWidget(self.btn_del)
        v.addLayout(h2)

        if self.role != "admin":
            self.btn_add.setEnabled(False)
            self.btn_del.setEnabled(False)

        self.setLayout(v)
        self.load_filters()
        self.load()

    def load_filters(self):
        conn = get_connection()
        if not conn: return
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM centers ORDER BY name;")
        for r in cur.fetchall():
            self.center.addItem(r[1], r[0])
        cur.execute("SELECT id, name FROM items WHERE item_type='Расход' ORDER BY code;")
        for r in cur.fetchall():
            self.item.addItem(r[1], r[0])
        cur.close(); conn.close()

    def load(self):
        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Нет связи с БД")
            return
        cur = conn.cursor()
        cur.execute("""
            SELECT l.id, c.name, i.name, l.limit_value, COALESCE(SUM(r.actual),0)
            FROM limits l
            JOIN centers c ON l.center_id=c.id
            JOIN items i ON l.item_id=i.id
            LEFT JOIN records r ON l.center_id=r.center_id AND l.item_id=r.item_id AND l.period=r.period
            GROUP BY l.id, c.name, i.name, l.limit_value
            ORDER BY c.name;
        """)
        rows = cur.fetchall()
        self.table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            lim = float(r[3])
            used = float(r[4])
            pct = (used/lim*100) if lim else 0
            st = "В норме" if pct < 80 else ("Предупреждение" if pct < 100 else "ПРЕВЫШЕНО")
            for j in range(5):
                self.table.setItem(i, j, QTableWidgetItem(str(r[j])))
            self.table.setItem(i, 5, QTableWidgetItem(st))
        cur.close(); conn.close()

    def on_click(self, row, col):
        self.sel_id = self.table.item(row, 0).text()

    def add(self):
        if self.role != "admin": return
        cid = self.center.currentData()
        iid = self.item.currentData()
        per = self.period.date().toString("yyyy-MM")
        lim = self.limit.value()
        if not cid or not iid:
            QMessageBox.warning(self, "Ошибка", "Выберите центр и статью")
            return
        conn = get_connection()
        if not conn: return
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO limits (center_id,item_id,period,limit_value)
                VALUES (%s,%s,%s,%s)
                ON CONFLICT (center_id,item_id,period) DO UPDATE SET limit_value=EXCLUDED.limit_value;
            """, (cid, iid, per, lim))
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
            cur.execute("DELETE FROM limits WHERE id=%s;", (self.sel_id,))
            conn.commit(); self.sel_id=None; self.load()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            cur.close(); conn.close()
