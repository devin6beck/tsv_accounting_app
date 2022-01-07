from Utils.list_and_dicts import safe_data, special_data
from PyQt6 import QtGui
import difflib


class Inspect:

    def __init__(self, ui, siriusware, fusebox):
        self.ui = ui
        self.siriusware = siriusware
        self.fusebox = fusebox

    def total(self):
        # The methods called below return None if there was an error calculating the over/short for a particular.
        # Otherwise they return a number describing the difference between what the Siriusware Csv file says a
        # pc_descrip key's value is and what will be stored in the newly created Daily.xlsx for that pc_descrip key.
        # Pc_descrip keys can be found in list_and_dict_.py
        over_short_cc = self.credit_cards()
        over_short_cash = self.special('CASH', self.ui.cash_deposit_lineEdit.text())
        over_short_check = self.special('CHECK', self.ui.check_deposit_lineEdit.text())
        over_short_check_request = self.special('CHECK REQUEST', self.ui.check_request_lineEdit.text())
        over_short_square = self.square()
        over_short_unknown = self.unknown()

        # Calculate over/short total. over_short_check_request is subtracted do the daily subtracting check_request
        # in D41 and J40 of the Daily.xlsx.
        try:
            over_short_total = (over_short_cc + over_short_cash + over_short_check - over_short_check_request
                                + over_short_square + over_short_unknown)
            self.ui.inpectResultsBrowser.setTextColor(QtGui.QColor('Purple'))
            # Show over/short rounded to second decimal in browser
            self.ui.inpectResultsBrowser.append(" ")
            self.ui.inpectResultsBrowser.append(f'Over/Short = {round(over_short_total, 2)}')
            return over_short_total
        except TypeError:
            self.ui.inpectResultsBrowser.setTextColor(QtGui.QColor('Purple'))
            self.ui.inpectResultsBrowser.append(" ")
            self.ui.inpectResultsBrowser.append('Over/Short = Error...Check input fields and make sure they only '
                                                'include numbers or are left blank')
            return False

    # This method returns a number describing the difference between what the Siriusware Csv file says the credit card
    # values are and what the Fusebox Csv file says the credit card values are.
    def credit_cards(self):
        over_short_cc = 0
        # Siriusware_cc_dict = a dictionary of keys for card name and values of card.
        # If there is no value for the card then the value is defaulted to 0.
        # Value comes out as negative in siriusware so have to turn to positive.
        siriusware_cc_dict = {'MC': -self.siriusware.dictionary.get('MASTERCARD', 0),
                              'VI': -self.siriusware.dictionary.get('VISA', 0),
                              'DI': -self.siriusware.dictionary.get('DISCOVER', 0),
                              'AX': -self.siriusware.dictionary.get('AMERICAN EXPRESS', 0)}

        # If fusebox does not match siriusware_cc_dict find the values that do not match.
        if self.fusebox.dictionary != siriusware_cc_dict:
            # fk = fusebox key, fv = fusebox value, sk = siriusware key, sv = siriusware value
            for fk, fv in self.fusebox.dictionary.items():
                for sk, sv in siriusware_cc_dict.items():
                    if fk == sk and fv != sv:
                        # Puts a message in the browser showing what Fusebox says a credit card amount should equal vs
                        # what Siriusware says it should equal. It also shows how much the difference is.
                        self.msg_cc_discrepancy(fk, fv, sk, sv)
                        over_short_cc += fv - sv
            return over_short_cc

        # Positive message to browser saying Fusebox credit card amounts match Siriusware credit card amounts.
        self.msg_cc_match()
        return over_short_cc

    # The method called below returns None if there was an error calculating the over/short for a particular pc_descrip
    # key. Otherwise it returns a number describing the difference between what the Siriusware Csv file says a
    # pc_descrip key's value is and what will be stored in the newly created Daily.xlsx for that pc_descrip key using
    # user_input.
    def special(self, pc_descrip, user_input):
        # Set over_short_x to 0 from the start
        over_short_x = 0

        #  Check to see if user_input is blank. If blank then make user_input 0
        if user_input.strip(" ") == "":
            user_input = 0

        # Make sure the user input can be made a float
        try:
            user_input = float(user_input)

        except ValueError:
            self.ui.inpectResultsBrowser.setTextColor(QtGui.QColor('Red'))
            self.ui.inpectResultsBrowser.append('Input for ' + f"'{pc_descrip}'" + ' must only have numbers yet '
                                                + f"'{user_input}'" + ' was put for ' + f"'{pc_descrip}'")
            return

        if pc_descrip not in self.siriusware.dictionary:
            sv = 0
            if user_input != 0:
                self.msg_special_discrepancy(pc_descrip, user_input, sv)
                over_short_x = user_input
            return over_short_x

        # Assign sv to the value of what siriusware says pc_descrip is
        sv = float(self.siriusware.dictionary[pc_descrip])

        # Change from negative to positive for comparison, unless CHECK REQUEST
        if pc_descrip != 'CHECK REQUEST':
            sv = -sv

        # If siriusware's value does not match the user input for this pc_descrip
        if sv != float(user_input):
            # Error message to browser
            self.msg_special_discrepancy(pc_descrip, user_input, sv)

            over_short_x += user_input - sv
            return over_short_x

        # Positive message to browser
        self.ui.inpectResultsBrowser.setTextColor(QtGui.QColor('Green'))
        self.ui.inpectResultsBrowser.append(f"Input for {pc_descrip} matches Siriusware :)")
        self.ui.inpectResultsBrowser.append(' ')
        return over_short_x

    # The method called below returns None if there was an error calculating the over/short for the "SNOWSPORT SQUARE"
    # pc_descrip key. Otherwise it returns a number describing the difference between what the Siriusware Csv file says
    # "SNOWSPORT SQUARE" value is and what will be stored in the newly created Daily.xlsx "Snowsport Gross" cell using
    # user_input.
    def square(self):
        over_short_square = 0
        gross_input = self.ui.sq_gross_lineEdit.text()

        # Check to see if input is blank. If it is blank then assign 0 as the value
        if gross_input.strip(" ") == "":
            gross_input = 0

        # Make sure that the gross input lineEdit has numbers only
        try:
            gross_input = float(gross_input)

        except ValueError:
            self.ui.inpectResultsBrowser.setTextColor(QtGui.QColor('Red'))
            self.ui.inpectResultsBrowser.append('Input for SQUARE must only have numbers. Check input for Square'
                                                'Gross and Square Fee then try again.')
            return

        # Check to see if 'SNOWSPORT SQUARE' not in siriusware
        if 'SNOWSPORT SQUARE' not in self.siriusware.dictionary:

            # Check to see if there is input for Square. If there is no Square in Siriusware there should be no input.
            if gross_input != 0:
                self.ui.inpectResultsBrowser.setTextColor(QtGui.QColor('Red'))
                self.ui.inpectResultsBrowser.append(f'Siriusware says SQUARE GROSS should be $0 yet a gross of '
                                                    f'${gross_input} was put for SQUARE.')
                self.ui.inpectResultsBrowser.setTextColor(QtGui.QColor('Purple'))
                self.ui.inpectResultsBrowser.append(f'SQUARE is off by: {gross_input}')
                over_short_square = gross_input
                return over_short_square

            # return over/short as 0 if snowsport square not in siriusware and input is 0
            return over_short_square

        # Switch siriusware value from negative to positive for comparison. Siriusware puts square as a negative
        gross_sirius = -self.siriusware.dictionary.get('SNOWSPORT SQUARE')

        # Compare user input to siriusware value
        if gross_input != gross_sirius:
            self.ui.inpectResultsBrowser.setTextColor(QtGui.QColor('Red'))
            self.ui.inpectResultsBrowser.append(f'Siriusware says SQUARE GROSS is {gross_sirius} yet a gross of'
                                                f' {gross_input} was put for Square.')
            self.ui.inpectResultsBrowser.setTextColor(QtGui.QColor('Purple'))
            self.ui.inpectResultsBrowser.append(f'SQUARE is off by: {gross_input - gross_sirius}')

            # return the difference between siriusware and input data for the over/short total
            over_short_square = gross_input - gross_sirius
            return over_short_square
        else:
            self.ui.inpectResultsBrowser.setTextColor(QtGui.QColor('Green'))
            self.ui.inpectResultsBrowser.append("Input for SQUARE GROSS matches Siriusware :)")
            return over_short_square

    # If there is a key in Siriusware's pc_descrip column that is not in the list_and_dicts.py data then the program
    # will not know what cell to store the value in the new created Daily.xlsx. Therefore we must let the user know
    # the value for that particular key must be manually inputted into the new created Daily.xlsx.
    # This method returns a number describing the difference between all the "Unknown"s key's values and 0.
    def unknown(self):
        # Inspect siriusware for an unknown pc_descrip.
        over_short_unknown = 0
        for k in self.siriusware.dictionary:

            # Match each siriusware key to a key in safe_data list
            pc_descrip = difflib.get_close_matches(k, safe_data, n=1)

            # If nothing is matched and k is also not in special_data then unknown value is siriusware[k]
            if len(pc_descrip) < 1 and k not in special_data:
                # Let the user know an "Unknown" pc_descrip key was found and the value for that key.
                self.ui.inpectResultsBrowser.setTextColor(QtGui.QColor('Red'))
                self.ui.inpectResultsBrowser.append(f'Unknown pc_descrip named {k} found. {k} will have to be '
                                                    f'manually inputted. {k} = {self.siriusware.dictionary[k]}')
                over_short_unknown += self.siriusware.dictionary[k]

        return over_short_unknown

    def msg_cc_discrepancy(self, fk, fv, sk, sv):
        self.ui.inpectResultsBrowser.setTextColor(QtGui.QColor('Red'))
        self.ui.inpectResultsBrowser.append(f'Fusebox says {fk} is ${fv} yet '
                                            f'Siriusware says {sk} is ${sv}')
        self.ui.inpectResultsBrowser.setTextColor(QtGui.QColor('Purple'))
        self.ui.inpectResultsBrowser.append(f'{fk} is off by: {round(fv - sv, 2)}')
        self.ui.inpectResultsBrowser.append(' ')

    def msg_cc_match(self):
        # Positive message to browser
        self.ui.inpectResultsBrowser.setTextColor(QtGui.QColor('Green'))
        self.ui.inpectResultsBrowser.append(f"Fusebox credit cards match Siriusware :)")
        # Put a blank line after credit cards are inspected.
        self.ui.inpectResultsBrowser.append(" ")

    def msg_special_discrepancy(self, pc_descrip, user_input, sv):
        self.ui.inpectResultsBrowser.setTextColor(QtGui.QColor('Red'))
        self.ui.inpectResultsBrowser.append(f"Siriusware says {pc_descrip} is ${sv} yet ${user_input} "
                                            f"was inputted for {pc_descrip}")
        self.ui.inpectResultsBrowser.setTextColor(QtGui.QColor('Purple'))
        self.ui.inpectResultsBrowser.append(f'{pc_descrip} is off by: {round(user_input - sv, 2)}')
        self.ui.inpectResultsBrowser.append(' ')