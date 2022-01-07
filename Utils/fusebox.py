from Utils.csv import Csv


class Fusebox(Csv):
    def __init__(self, QtWidget):
        super().__init__(QtWidget)
        self.dictionary = {"MC": 0, "VI": 0, "DI": 0, "AX": 0}

    def make_dictionary(self, description, amount):
        # Get values from fusebox and make a dictionary using the credit card names as the keys
        fusebox = {description[i]: amount[i] for i in range(len(description))}

        self.dictionary = {'MC': fusebox.get('MC', 0),
                   'VI': fusebox.get('VI', 0),
                   'DI': fusebox.get('DI', 0),
                   'AX': fusebox.get('AX', 0)}

