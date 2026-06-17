from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QTableWidget, QTableWidgetItem, QPushButton,
                              QComboBox, QDateEdit, QMessageBox, QHeaderView)
from PyQt5.QtCore import QDate
from database.db import get_connection

class AnalysisWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("План-факт анализ")
        self.resize(900, 500)
        v = QVBoxLayout()

        h = QHBoxLayout()
        h.addWidget(QLabel("Период:"))
        self.period = QDateEdit()
        self.period.setCalendarPopup(True)
        self.period.setDisplayFormat("yyyy-MM")
        self.period.setDate(QDate.currentDate().addDays(-7))
        h.addWidget(self.period)
        h.addWidget(QLabel("Сценарий:"))
        self.scenario = QComboBox()
        h.addWidget(self.scenario)
        btn = QPushButton("Показать")
        btn.clicked.connect(self.load)
        h.addWidget(btn)
        v.addLayout(h)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["Центр","Статья","Тип","План","Факт","Отклонение","%","Статус"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        v.addWidget(self.table)

        self.lbl = QLabel("Всего записей: 0 | выполнено: 0 | отклонения: 0 | критично: 0")
        v.addWidget(self.lbl)

        self.setLayout(v)
        self.load_filters()
        self.load()

    def load_filters(self):
        conn = get_connection()
        if not conn: return
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM scenarios ORDER BY name;")
        for r in cur.fetchall():
            self.scenario.addItem(r[1], r[0])
        cur.close(); conn.close()

    def load(self):
        per = self.period.date().toString("yyyy-MM")
        sid = self.scenario.currentData()
        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Нет связи с БД")
            return
        cur = conn.cursor()
        cur.execute("""
            SELECT c.name, i.name, i.item_type, r.planned, r.actual
            FROM records r
            JOIN centers c ON r.center_id=c.id
            JOIN items i ON r.item_id=i.id
            WHERE r.period=%s AND r.scenario_id=%s
            ORDER BY i.item_type DESC, i.code;
        """, (per, sid))
        rows = cur.fetchall()
        self.table.setRowCount(len(rows))
        good = warn = crit = 0
        dev_Доход = dev_Расход = 0
        for i, r in enumerate(rows):
            p = float(r[3] or 0)
            a = float(r[4] or 0)
            d = a - p
            pct = (d/p*100) if p else 0
            self.table.setItem(i, 0, QTableWidgetItem(r[0]))
            self.table.setItem(i, 1, QTableWidgetItem(r[1]))
            self.table.setItem(i, 2, QTableWidgetItem(r[2]))
            self.table.setItem(i, 3, QTableWidgetItem("{:.2f}".format(p)))
            self.table.setItem(i, 4, QTableWidgetItem("{:.2f}".format(a)))
            self.table.setItem(i, 5, QTableWidgetItem("{:.2f}".format(d)))
            self.table.setItem(i, 6, QTableWidgetItem("{:.1f}%".format(pct)))
            if r[2] == "Доход":
                dev_Доход += d
                st = "Выполнено" if d >= 0 else "Не выполнено"
                if d >= 0: good += 1
                else: warn += 1
            else:
                dev_Расход += d
                st = "Выполнено" if d <= 0 else "Перерасход"
                if d <= 0: good += 1
                else: crit += 1
            self.table.setItem(i, 7, QTableWidgetItem(st))
        cur.close(); conn.close()
        self.lbl.setText("Всего: {} | выполнено: {} | отклонения: {} | критично: {} | отклонение доходов: {:.2f} | расходов: {:.2f}".format(
            len(rows), good, warn, crit, dev_Доход, dev_Расход))
