from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QTableWidget, QTableWidgetItem, QPushButton,
                              QComboBox, QDateEdit, QMessageBox, QHeaderView)
from PyQt5.QtCore import QDate
from database.db import get_connection

class BDRWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("БДР - Бюджет Доходов и Расходов")
        self.resize(800, 500)
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
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Код","Статья","Тип","План","Факт","Отклонение"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        v.addWidget(self.table)

        self.lbl = QLabel("Итоги: доходы 0 | расходы 0 | прибыль 0")
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
        # Берем все статьи и ищем для них записи
        cur.execute("SELECT id, code, name, item_type FROM items ORDER BY code;")
        items = cur.fetchall()
        self.table.setRowCount(len(items))
        inc_plan = inc_fact = exp_plan = exp_fact = 0
        for i, it in enumerate(items):
            self.table.setItem(i, 0, QTableWidgetItem(it[1]))
            self.table.setItem(i, 1, QTableWidgetItem(it[2]))
            self.table.setItem(i, 2, QTableWidgetItem(it[3]))
            # Ищем запись
            cur.execute("SELECT planned, actual FROM records WHERE item_id=%s AND period=%s AND scenario_id=%s;",
                        (it[0], per, sid))
            row = cur.fetchone()
            p = float(row[0]) if row else 0
            a = float(row[1]) if row else 0
            self.table.setItem(i, 3, QTableWidgetItem("{:.2f}".format(p)))
            self.table.setItem(i, 4, QTableWidgetItem("{:.2f}".format(a)))
            self.table.setItem(i, 5, QTableWidgetItem("{:.2f}".format(a-p)))
            if it[3] == "Доход":
                inc_plan += p; inc_fact += a
            else:
                exp_plan += p; exp_fact += a
        cur.close(); conn.close()
        profit = inc_plan - exp_plan
        self.lbl.setText("Итоги: доходы план {:.2f} факт {:.2f} | расходы план {:.2f} факт {:.2f} | прибыль {:.2f}".format(
            inc_plan, inc_fact, exp_plan, exp_fact, profit))
