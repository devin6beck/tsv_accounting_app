import sys
from Utils.Tsv_Accounting_App_Ui import Ui_MainWindow
from PyQt6 import QtWidgets, QtCore
from Utils.buttons_manager import ButtonsManager


class App(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.manager = ButtonsManager(self.ui, self,)

        # Set date fields to today's date
        self.ui.daily_date_edit.setDate(QtCore.QDate.currentDate())
        self.ui.todays_date_edit.setDate(QtCore.QDate.currentDate())

        self.ui.fuseboxButton.clicked.connect(self.manager.load_fusebox)
        self.ui.siriuswareButton.clicked.connect(self.manager.load_siriusware)
        self.ui.inspectButton.clicked.connect(self.manager.inspect)
        self.ui.finishButton.clicked.connect(self.manager.finish)

    # this makes it so errors are shown when using Qtdesigner
    def except_hook(self, cls, exception, traceback):
        sys.__excepthook__(cls, exception, traceback)

    # this makes it so errors are shown in Terminal when using Qtdesigner
    sys.excepthook = except_hook


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    widget = App()
    widget.show()
    app.exec()
