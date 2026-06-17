from PyQt5.QtWidgets import QFileDialog, QMessageBox

def export(table, parent):
    fname, _ = QFileDialog.getSaveFileName(parent, "Сохранить", "", "CSV (*.csv)")
    if not fname:
        return
    try:
        with open(fname, 'w', encoding='utf-8-sig') as f:
            hdr = []
            for c in range(table.columnCount()):
                it = table.horizontalHeaderItem(c)
                hdr.append(it.text() if it else "")
            f.write(";".join(hdr) + "\n")
            for r in range(table.rowCount()):
                row = []
                for c in range(table.columnCount()):
                    it = table.item(r, c)
                    row.append(it.text() if it else "")
                f.write(";".join(row) + "\n")
        QMessageBox.information(parent, "Успех", "Сохранено: " + fname)
    except Exception as e:
        QMessageBox.critical(parent, "Ошибка", str(e))
