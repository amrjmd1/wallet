import sys
from os import path
import sqlite3
from openpyxl import Workbook

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.uic import loadUiType

FORM_CLASS, _ = loadUiType(path.join(path.dirname(__file__), 'wallet.ui'))


class mainapp(QMainWindow, FORM_CLASS):
    def __init__(self, parent=None):
        super(mainapp, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.handel_ui()

        global conn
        conn = sqlite3.connect('wallet.db')
        global c
        c = conn.cursor()

        c.execute(
            '''CREATE TABLE IF NOT EXISTS activity
            (ID INTEGER PRIMARY KEY AUTOINCREMENT,
            TIME DATETIME DEFAULT CURRENT_TIMESTAMP,
            VALUE real, TYPE text,
             NOTE text)''')

        self.btn_addnew.clicked.connect(self.add_new)
        self.btn_brows.clicked.connect(self.save_location)
        self.btn_export.clicked.connect(self.export_excel)
        self.in_value.valueChanged.connect(self.handel_style)
        self.in_location.textChanged.connect(self.handel_export_btn)
        self.load_data()
        self.show_data()
        self.in_time.currentIndexChanged.connect(self.show_data)
        self.in_type_export.currentIndexChanged.connect(self.show_data)

    def handel_style(self):
        self.in_value.setStyleSheet('border-width: 0')

    def handel_ui(self):
        self.setWindowTitle('wallet')
        self.setFixedSize(640, 700)
        self.tableWidget.setColumnWidth(0, 40)
        self.tableWidget.setColumnWidth(1, 150)
        self.tableWidget.setColumnWidth(4, 200)
        self.TB_export.setColumnWidth(0, 40)
        self.TB_export.setColumnWidth(1, 150)
        self.TB_export.setColumnWidth(4, 200)

    def add_new(self):
        value = float(self.in_value.text()) if self.in_value.text() else 0
        note = self.in_note.toPlainText()
        type = self.in_type.currentText()
        if value > 0:
            c.execute('INSERT INTO activity (VALUE ,TYPE ,NOTE) VALUES (?,?,?)', (value, type, note))
            conn.commit()
            self.in_value.setValue(00.00)
            self.in_note.clear()
            self.load_data()
        else:
            self.in_value.setStyleSheet('border-width: 1px; border-color: red;border-style: solid;')

    def load_data(self):
        self.tableWidget.setRowCount(0)
        result = c.execute(
            '''SELECT * FROM activity 
            WHERE TIME BETWEEN datetime('now', '-1 months') 
            AND datetime('now', 'localtime')
             ORDER BY TIME DESC LIMIT 30''')  # last month

        for row, rowData in enumerate(result):
            self.tableWidget.insertRow(row)
            for colNumber, data in enumerate(rowData):
                item = QTableWidgetItem(str(data))
                if 4 != colNumber != 2:
                    item.setFlags(Qt.ItemIsEnabled)
                self.tableWidget.setItem(row, colNumber, item)

    def show_data(self):
        result = self.get_data()
        self.TB_export.setRowCount(0)
        for row, rowData in enumerate(result):
            self.TB_export.insertRow(row)
            for colNumber, data in enumerate(rowData):
                item = QTableWidgetItem(str(data))
                item.setFlags(Qt.ItemIsEnabled)
                self.TB_export.setItem(row, colNumber, item)

    def get_data(self):
        time = self.in_time.currentIndex()
        type = self.in_type_export.currentIndex()
        time_q = ''
        type_q = '' if type == 3 else "TYPE = '%s'" % self.in_type_export.currentText()

        if time != 5:
            list_q = ['-6 days', '-1 months', '-3 months', '-6 months', '-12 months']
            time_q = "TIME BETWEEN datetime('now', '%s')AND datetime('now', 'localtime')" % list_q[time]

        where_q = 'WHERE' if type_q or time_q else ''
        and_q = 'AND' if type_q and time_q else ''
        return c.execute("SELECT * FROM activity %s %s %s %s ORDER BY TIME DESC" % (where_q, time_q, and_q, type_q))

    def save_location(self):
        save_location_name = QFileDialog.getSaveFileName(self, caption='Save At', directory='.', filter='All Files *.*')
        self.in_location.setText(save_location_name[0])

    def handel_export_btn(self):
        self.btn_export.setEnabled(True if self.in_location.text() else False)

    def export_excel(self):
        name = self.in_location.text()
        name = name.rstrip('.xlsx')
        if name:
            try:
                wb = Workbook()
                ws = wb.active
                data = self.get_data()
                for row in data:
                    ws.append(row)
                wb.save("%s.xlsx" % name)
            except Exception:
                QMessageBox.warning(self, 'Export error', 'your Export failed !')
                return
            QMessageBox.information(self, 'Export completed', 'your export completed at %s' % name)
            self.in_location.setText('')


# conn.close()


def main():
    app = QApplication(sys.argv)
    window = mainapp()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
