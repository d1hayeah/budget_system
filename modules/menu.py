from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton

class MenuWindow(QWidget):
    def __init__(self, username, role, user_id):
        super().__init__()
        self.role = role
        self.setWindowTitle("Меню")
        self.resize(400, 400)
        v = QVBoxLayout()
        v.addWidget(QLabel("Пользователь: " + username + " | Роль: " + role))

        buttons = [
            ("Центры ответственности", self.centers),
            ("Статьи бюджета", self.items),
            ("БДР", self.bdr),
            ("БДДС", self.bdds),
            ("План-факт анализ", self.analysis),
            ("Лимиты", self.limits),
            ("Сценарии", self.scenarios),
        ]
        if self.role == "admin":
            buttons.insert(2, ("Ввод план/факт", self.entry))

        for text, func in buttons:
            b = QPushButton(text)
            b.clicked.connect(func)
            v.addWidget(b)

        self.setLayout(v)

    def centers(self):
        from modules.centers import CentersWindow
        self.w = CentersWindow(self.role)
        self.w.show()

    def items(self):
        from modules.items import ItemsWindow
        self.w = ItemsWindow(self.role)
        self.w.show()

    def entry(self):
        from modules.entry import EntryWindow
        self.w = EntryWindow()
        self.w.show()

    def bdr(self):
        from modules.bdr import BDRWindow
        self.w = BDRWindow()
        self.w.show()

    def bdds(self):
        from modules.bdds import BDDSWindow
        self.w = BDDSWindow()
        self.w.show()

    def analysis(self):
        from modules.analysis import AnalysisWindow
        self.w = AnalysisWindow()
        self.w.show()

    def limits(self):
        from modules.limits import LimitsWindow
        self.w = LimitsWindow(self.role)
        self.w.show()

    def scenarios(self):
        from modules.scenarios import ScenariosWindow
        self.w = ScenariosWindow()
        self.w.show()
