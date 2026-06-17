from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QTableWidget, QTableWidgetItem, QPushButton,
                              QLineEdit, QDoubleSpinBox, QMessageBox, QHeaderView)
from database.db import get_connection

class ScenariosWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Сценарное моделирование")
        self.resize(800, 500)
        v = QVBoxLayout()

        h = QHBoxLayout()
        h.addWidget(QLabel("Название:"))
        self.name = QLineEdit()
        h.addWidget(self.name)
        h.addWidget(QLabel("Описание:"))
        self.desc = QLineEdit()
        h.addWidget(self.desc)
        v.addLayout(h)

        h2 = QHBoxLayout()
        h2.addWidget(QLabel("Изменение доходов %:"))
        self.inc = QDoubleSpinBox()
        self.inc.setRange(-50, 50)
        h2.addWidget(self.inc)
        h2.addWidget(QLabel("Изменение расходов %:"))
        self.exp = QDoubleSpinBox()
        self.exp.setRange(-50, 50)
        h2.addWidget(self.exp)
        btn = QPushButton("Создать из базового")
        btn.clicked.connect(self.create)
        h2.addWidget(btn)
        v.addLayout(h2)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID","Название","Описание","Базовый"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        v.addWidget(self.table)

        btn2 = QPushButton("Сравнить с базовым")
        btn2.clicked.connect(self.compare)
        v.addWidget(btn2)

        self.res = QTableWidget()
        self.res.setColumnCount(4)
        self.res.setHorizontalHeaderLabels(["Статья","Базовый","Сценарий","Изменение"])
        self.res.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        v.addWidget(self.res)

        self.setLayout(v)
        self.load_list()

    def load_list(self):
        conn = get_connection()
        if not conn: return
        cur = conn.cursor()
        cur.execute("SELECT id, name, description, is_base FROM scenarios ORDER BY id;")
        rows = cur.fetchall()
        self.table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(str(r[0])))
            self.table.setItem(i, 1, QTableWidgetItem(r[1]))
            self.table.setItem(i, 2, QTableWidgetItem(r[2] or ""))
            self.table.setItem(i, 3, QTableWidgetItem("Да" if r[3] else "Нет"))
        cur.close(); conn.close()

    def create(self):
        n = self.name.text().strip()
        if not n:
            QMessageBox.warning(self, "Ошибка", "Введите название")
            return
        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Нет связи с БД")
            return
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO scenarios (name, description, is_base) VALUES (%s,%s,FALSE) RETURNING id;",
                        (n, self.desc.text()))
            new_id = cur.fetchone()[0]
            # Копируем базовый сценарий с корректировкой
            cur.execute("SELECT id FROM scenarios WHERE is_base=TRUE LIMIT 1;")
            base_id = cur.fetchone()[0]
            cur.execute("""
                INSERT INTO records (center_id, item_id, period, planned, actual, scenario_id)
                SELECT center_id, item_id, period,
                    CASE WHEN i.item_type='Доход' THEN planned*(1+%s/100) ELSE planned*(1+%s/100) END,
                    0, %s
                FROM records r JOIN items i ON r.item_id=i.id WHERE r.scenario_id=%s;
            """, (self.inc.value(), self.exp.value(), new_id, base_id))
            conn.commit()
            QMessageBox.information(self, "Успех", "Сценарий создан")
            self.load_list()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            cur.close(); conn.close()

    def compare(self):
        conn = get_connection()
        if not conn: return
        cur = conn.cursor()
        cur.execute("SELECT id FROM scenarios WHERE is_base=TRUE LIMIT 1;")
        base_id = cur.fetchone()[0]
        # Берем последний созданный небазовый
        cur.execute("SELECT id FROM scenarios WHERE is_base=FALSE ORDER BY id DESC LIMIT 1;")
        row = cur.fetchone()
        if not row:
            QMessageBox.information(self, "Инфо", "Нет сценариев для сравнения")
            cur.close(); conn.close()
            return
        scen_id = row[0]
        cur.execute("""
            SELECT i.name, i.item_type,
                COALESCE((SELECT planned FROM records WHERE item_id=i.id AND scenario_id=%s LIMIT 1),0),
                COALESCE((SELECT planned FROM records WHERE item_id=i.id AND scenario_id=%s LIMIT 1),0)
            FROM items i ORDER BY i.code;
        """, (base_id, scen_id))
        rows = cur.fetchall()
        self.res.setRowCount(len(rows))
        for i, r in enumerate(rows):
            base = float(r[2])
            scen = float(r[3])
            self.res.setItem(i, 0, QTableWidgetItem(r[0]))
            self.res.setItem(i, 1, QTableWidgetItem("{:.2f}".format(base)))
            self.res.setItem(i, 2, QTableWidgetItem("{:.2f}".format(scen)))
            self.res.setItem(i, 3, QTableWidgetItem("{:.2f}".format(scen-base)))
        cur.close(); conn.close()
