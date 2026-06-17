from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QTableWidget, QTableWidgetItem, QPushButton,
                              QComboBox, QDateEdit, QMessageBox, QHeaderView)
from PyQt5.QtCore import QDate
from database.db import get_connection

class BDDSWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("БДДС - Движение денежных средств")
        self.resize(700, 400)
        v = QVBoxLayout()

        h = QHBoxLayout()
        h.addWidget(QLabel("Период:"))
        self.period = QDateEdit()
        self.period.setCalendarPopup(True)
        self.period.setDisplayFormat("yyyy-MM")
        self.period.setDate(QDate.currentDate().addDays(-7))
        h.addWidget(self.period)
        h.addWidget(QLabel("Режим:"))
        self.mode = QComboBox()
        self.mode.addItems(["План", "Факт"])
        h.addWidget(self.mode)
        btn = QPushButton("Показать")
        btn.clicked.connect(self.load)
        h.addWidget(btn)
        v.addLayout(h)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Период","Приток","Отток","Баланс"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        v.addWidget(self.table)

        self.lbl = QLabel("Всего приток: 0 | отток: 0 | баланс: 0")
        v.addWidget(self.lbl)

        self.setLayout(v)
        self.load()

    def load(self):
        per = self.period.date().toString("yyyy-MM")
        mode = "planned" if self.mode.currentText()=="План" else "actual"
        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Нет связи с БД")
            return
        cur = conn.cursor()
        # Считаем доходы и расходы
        cur.execute("""
            SELECT COALESCE(SUM(r.{0}),0) FROM records r
            JOIN items i ON r.item_id=i.id
            WHERE r.period=%s AND i.item_type='Доход';
        """.format(mode), (per,))
        inflow = float(cur.fetchone()[0])
        cur.execute("""
            SELECT COALESCE(SUM(r.{0}),0) FROM records r
            JOIN items i ON r.item_id=i.id
            WHERE r.period=%s AND i.item_type='Расход';
        """.format(mode), (per,))
        outflow = float(cur.fetchone()[0])
        cur.close(); conn.close()
        bal = inflow - outflow
        self.table.setRowCount(1)
        self.table.setItem(0, 0, QTableWidgetItem(per))
        self.table.setItem(0, 1, QTableWidgetItem("{:.2f}".format(inflow)))
        self.table.setItem(0, 2, QTableWidgetItem("{:.2f}".format(outflow)))
        self.table.setItem(0, 3, QTableWidgetItem("{:.2f}".format(bal)))
        self.lbl.setText("Всего приток: {:.2f} | отток: {:.2f} | баланс: {:.2f}".format(inflow, outflow, bal))
