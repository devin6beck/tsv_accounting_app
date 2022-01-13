from PyQt6.QtWidgets import QFileDialog
import pandas as pd
from PyQt6 import QtWidgets


class Csv:
    def __init__(self, QtWidget):
        self.QtWidget = QtWidget

    def upload(self, key_title, value_title, check_box, line_edit):
        self.file_name = QFileDialog.getOpenFileName(
            caption="Open CSV File",
            filter="CSV Files, *.csv")[0]

        # If the user presses cancel we want to return None
        if len(self.file_name) == 0:
            return None

        if not self.make_list(key_title, value_title):
            self.error_upload_message(key_title, value_title, check_box, line_edit)
            return False

        # If the program can make a dictionary out of the descrip column and amt column return True.
        return True

    def make_list(self, key_title, value_title):
        data = pd.read_csv(self.file_name)

        for column in data:

            # Make the column title lowercase and split the string at the comma
            split_k = column.lower().split(",", 1)

            # If the descrip given as a parameter matches the first word in the slit string list then make a list
            # from what is in the description column
            if key_title in split_k[0]:
                description = data[column].tolist()

            # If the amt given as a parameter matches the first word in the slit string list then make a list
            # from what is in the amount column
            if value_title in split_k[0]:
                amount = data[column].tolist()

        try:
            self.make_dictionary(description, amount)
            return True

        except UnboundLocalError:
            print("UnboundLocalError in csv_file")
            return False

    def make_dictionary(self, description, amount):
        # Get values from fusebox and make a dictionary using the credit card names as the keys
        self.dictionary = {description[i]: amount[i] for i in range(len(description))}


    # Change it so that QtWidget is given as a parameter when Csv() is made. call self.QtWidget here instead when it
    # is fixed
    def error_upload_message(self, key, value, check_box, line_edit):
        # Add error message to lineEdit and uncheck the checkbox.
        line_edit.setText("Error uploading file. Try again")
        check_box.setChecked(False)
        # Make a QMessageBox warning
        QtWidgets.QMessageBox.warning(self.QtWidget, f'Upload Error',
                                      f"CSV file missing {key} or {value} column. Try Again")

    # This adds the file name to the lineEdit given and checkmarks the checkbox given as a parameter
    def upload_pos(self, csv_file, checkbox, line_edit):
        checkbox.setChecked(True)
        line_edit.setText(csv_file.file_name)
