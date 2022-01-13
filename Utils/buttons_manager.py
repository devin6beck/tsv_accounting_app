from Utils.fusebox import Fusebox
from Utils.csv import Csv
from Utils.inspect import Inspect
from Utils.finish import Finish
from PyQt6 import QtWidgets


class ButtonsManager:

    def __init__(self, ui, QtWidget):
        self.ui = ui
        self.QtWidget = QtWidget
        self.fusebox = Fusebox(QtWidget)
        self.siriusware = Csv(QtWidget)

    # If the we can make a dictionary from the uploaded file then a checkmark is applied and the file name is
    # stored in the lineEdit.
    def load_fusebox(self):
        answer = self.fusebox.upload("payment_type", "amount", self.ui.upload_fusebox_checkBox, self.ui.fuseboxLineEdit)

        if answer is None:
            return

        if answer is False:
            # If user uploaded a Fusebox file that created a dictionary and then tried to upload a file that failed
            # we want the dictionary to be reset to the default dictionary with 0 as values for credit cards
            self.fusebox.dictionary = {"MC": 0, "VI": 0, "DI": 0, "AX": 0}
            return

        # Put checkbox to True and store file name on lineEdit
        self.fusebox.upload_pos(self.fusebox,
                                self.ui.upload_fusebox_checkBox,
                                self.ui.fuseboxLineEdit)

    # Method used when Siriusware Upload Button is clicked
    # If the we can make a dictionary from the uploaded file then a checkmark is applied, the file name is
    # stored in the lineEdit, the inspectButton is enabled, and the finishButton is enabled.
    def load_siriusware(self):
        answer = self.siriusware.upload("pc_descrip", "amount", self.ui.upload_siriusware_checkBox,
                                        self.ui.siriuswareLineEdit)

        if answer is None:
            return

        if answer is False:
            # Disable the inspectButton and finishButton if the Siriusware upload caused error.
            self.ui.inspectButton.setEnabled(False)
            self.ui.finishButton.setEnabled(False)
            return

        # Put checkbox to True and store file name on lineEdit
        self.siriusware.upload_pos(self.siriusware,
                                   self.ui.upload_siriusware_checkBox,
                                   self.ui.siriuswareLineEdit)

        # Enable the inspectButton and finishButton
        self.ui.inspectButton.setEnabled(True)
        self.ui.finishButton.setEnabled(True)

    def inspect(self):
        # Clear the Broswer
        self.ui.inpectResultsBrowser.setText('')

        inspect = Inspect(self.ui, self.siriusware, self.fusebox)

        # This returns False if there is an error calculating the over/short total.
        # Else returns the over/short total
        return inspect.total()

    def finish(self):
        finish = Finish(self.ui, self, self.siriusware, self.fusebox)

        # User must check the ADS or CHS radioButton before finishing.
        if self.ui.ads_radioButton.isChecked() is False and self.ui.chs_radioButton.isChecked() is False:
            QtWidgets.QMessageBox.warning(self.QtWidget, 'ADS or CHS?',
                                          "Choose ADS or CHS before pressing finish")
            return

        # Check self.inspect() before finishing just in case the user did not press inspect button.
        # If the over/short can not be calculated then show the user and error message and return to app.
        if self.inspect() is False:
            QtWidgets.QMessageBox.critical(self.QtWidget, 'Error', "Over/Short can not be calculated. "
                                                                   "Check and make sure input fields only have numbers")
            return

        # Open BLANK_Daily.xlsx > store values from siriusware and fusebox dictionaries in proper cells > store user
        # input from lineEdits in proper cells> Save file > Open file > Exit app
        finish.finish()
