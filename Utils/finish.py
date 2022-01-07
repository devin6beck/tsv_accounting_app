import openpyxl
from Utils.list_and_dicts import special_data, safe_data
from PyQt6 import QtWidgets, QtCore, QtGui
import difflib
import os
import sys


daily = openpyxl.load_workbook("Utils/blank_daily.xlsx")

# Add special data to daily. line_edit is user input and cell is where it belongs in the daily excel.
def add_special_data(line_edit, cell):
    if line_edit.strip(" ") != "":
        daily.active[cell] = float(line_edit)

class Finish():

    def __init__(self, ui, QtWidget, siriusware, fusebox):
        self.ui = ui
        self.QtWidget = QtWidget
        self.siriusware = siriusware
        self.fusebox = fusebox

    def finish(self):
        # takes input out of lineEdits/date_edit and Adds name to new daily
        daily.active["C3"] = self.ui.name_lineEdit.text()
        daily.active["I3"] = self.ui.todays_date_edit.text()

        # Special data like credit card totals and user input totals need to go on the ADS side or CHS side depending
        # on what radioButton the user checks. Special data is stored in the daily.active here.

        if self.ui.ads_radioButton.isChecked() is True:
            # Parameters are the ADS specific cells in the daily.active file
            self.store_special_data("J31", "J32", "J40", "J42", "J43", "J37", "J38")
            # radio is used later when saving the file. It lets the program know what string to put at the start
            # of the file name
            radio = 'ADS'

        else:
            # Parameters are the CHS specific cells in the daily.active file
            self.store_special_data("D32", "D33", "D41", "D43", "D44", "D38", "D39")
            # radio is used later when saving the file. It lets the program know what string to put at the start
            # of the file name
            radio = 'CHS'

        self.store_safe_data()

        # Change date format to MMddyy example: Dec 30, 2021 = 123021
        self.ui.daily_date_edit.setDisplayFormat("MMddyy")

        # Make a name for the file. example: CHS123021.xlsx
        daily_name = radio + str(self.ui.daily_date_edit.text()) + '.xlsx'

        # Save file > Open file > Exit app
        daily.save(daily_name)
        os.startfile(daily_name)
        sys.exit()


    def store_special_data(self, cash_cell, check_deposit_cell, check_request_cell, sq_gross_cell, sq_fee_cell, mc_vi_di_cell, amx_cell):
        add_special_data(self.ui.cash_deposit_lineEdit.text(), cash_cell)
        add_special_data(self.ui.check_deposit_lineEdit.text(), check_deposit_cell)
        add_special_data(self.ui.check_request_lineEdit.text(), check_request_cell)
        add_special_data(self.ui.sq_gross_lineEdit.text(), sq_gross_cell)
        add_special_data(self.ui.sq_fee_lineEdit.text(), sq_fee_cell)

        # Add fusebox values to the daily on ADS side
        daily.active[mc_vi_di_cell] = self.fusebox.dictionary['MC'] + self.fusebox.dictionary['VI'] + self.fusebox.dictionary[
            'DI']
        daily.active[amx_cell] = self.fusebox.dictionary['AX']

    def store_safe_data(self):
        for k in self.siriusware.dictionary:
            pc_descrip = difflib.get_close_matches(k, safe_data, n=1)
            if len(pc_descrip) >= 1:
                daily.active[safe_data[pc_descrip[0]]] = self.siriusware.dictionary[k]
                # add_safe_data(safe_data[pc_descrip[0]], self.siriusware.dictionary[k])
            elif k not in special_data:
                QtWidgets.QMessageBox.warning(self.QtWidget, 'Unknown PC_DESCRIP', f'{k} will have to be manually inputted')
