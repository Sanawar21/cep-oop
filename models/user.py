from bank_details import BankDetails


class User:
    """
    User object for handling users in the store. 
    Every User has a unique username.
    """

    def __init__(self, username, password, full_name, address) -> None:
        self.username = username
        self.password = password
        self.full_name = full_name
        self.address = address

    def add_bank_details(self, bank_name, card_number, pin):

        valid_card_number = all([chr in "0123456789" for chr in card_number])
        valid_pin = all([chr in "0123456789" for chr in pin]) and len(pin) == 4

        if valid_card_number and valid_pin:
            self.bank_details = BankDetails(
                self.username, bank_name, card_number, pin)
            return self.bank_details


class Admin(User):

    def __init__(self) -> None:
        super().__init__("admin", "shopping123", "Admin",
                         "CIS Department, NED University, Karachi.")
