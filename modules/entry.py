from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QTableWidget, QTableWidgetItem, QPushButton,
                              QComboBox, QDateEdit, QDoubleSpinBox, QMessageBox, QHeaderView)
from PyQt5.QtCore import QDate
from database.db import get_connection

class EntryWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ввод план/факт")
        self.resize(800, 500)
        v = QVBoxLayout()

        # Фильтры
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
        h.addWidget(QLabel("Сценарий:"))
        self.scenario = QComboBox()
        h.addWidget(self.scenario)
        v.addLayout(h)

        # Поля ввода
        h2 = QHBoxLayout()
        h2.addWidget(QLabel("План:"))
        self.plan = QDoubleSpinBox()
        self.plan.setMaximum(99999999)
        h2.addWidget(self.plan)
        h2.addWidget(QLabel("Факт:"))
        self.fact = QDoubleSpinBox()
        self.fact.setMaximum(99999999)
        h2.addWidget(self.fact)
        self.btn_save = QPushButton("Сохранить")
        self.btn_save.clicked.connect(self.save)
        h2.addWidget(self.btn_save)
        v.addLayout(h2)

        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID","Центр","Статья","Период","Сценарий","План","Факт"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        v.addWidget(self.table)

        self.setLayout(v)
        self.load_filters()
        self.load_table()

    def load_filters(self):
        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Нет связи с БД")
            return
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM centers ORDER BY name;")
        for r in cur.fetchall():
            self.center.addItem(r[1], r[0])
        cur.execute("SELECT id, name FROM items ORDER BY code;")
        for r in cur.fetchall():
            self.item.addItem(r[1], r[0])
        cur.execute("SELECT id, name FROM scenarios ORDER BY name;")
        for r in cur.fetchall():
            self.scenario.addItem(r[1], r[0])
        cur.close(); conn.close()

    def save(self):
        cid = self.center.currentData()
        iid = self.item.currentData()
        per = self.period.date().toString("yyyy-MM")
        sid = self.scenario.currentData()
        if not cid or not iid:
            QMessageBox.warning(self, "Ошибка", "Выберите центр и статью")
            return
        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Нет связи с БД")
            return
        cur = conn.cursor()
        try:
            # Проверяем есть ли запись
            cur.execute("SELECT id FROM records WHERE center_id=%s AND item_id=%s AND period=%s AND scenario_id=%s;",
                        (cid, iid, per, sid))
            row = cur.fetchone()
            if row:
                cur.execute("UPDATE records SET planned=%s, actual=%s WHERE id=%s;",
                            (self.plan.value(), self.fact.value(), row[0]))
            else:
                cur.execute("INSERT INTO records (center_id,item_id,period,planned,actual,scenario_id) VALUES (%s,%s,%s,%s,%s,%s);",
                            (cid, iid, per, self.plan.value(), self.fact.value(), sid))
            conn.commit()
            QMessageBox.information(self, "Успех", "Сохранено")
            self.load_table()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            cur.close(); conn.close()

    def load_table(self):
        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Нет связи с БД")
            return
        cur = conn.cursor()
        cur.execute("""
            SELECT r.id, c.name, i.name, r.period, s.name, r.planned, r.actual
            FROM records r
            JOIN centers c ON r.center_id = c.id
            JOIN items i ON r.item_id = i.id
            JOIN scenarios s ON r.scenario_id = s.id
            ORDER BY r.period, c.name, i.code;
        """)
        rows = cur.fetchall()
        self.table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            for j in range(7):
                val = str(r[j])
                if j in (5,6):
                    val = "{:.2f}".format(float(r[j]))
                self.table.setItem(i, j, QTableWidgetItem(val))
        cur.close(); conn.close()
