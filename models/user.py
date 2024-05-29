from .bank_details import BankDetails


class User:
    """
    User object for handling users in the store. 
    Every User has a unique username.
    """

    def __init__(self, username, password, full_name, address, bank_details=None) -> None:
        self.username = username
        self.password = password
        self.full_name = full_name
        self.address = address
        self.bank_details = bank_details

    @classmethod
    def from_dict(cls, data):
        username = data["username"]
        password = data["password"]
        full_name = data["full_name"]
        address = data["address"]
        bank_details = BankDetails.from_dict(
            data["bank_details"]) if data["bank_details"] else None
        return cls(username, password, full_name, address, bank_details)

    def to_dict(self):
        return {
            "username": self.username,
            "password": self.password,
            "full_name": self.full_name,
            "address": self.address,
            "bank_details": self.bank_details.to_dict() if self.bank_details else None
        }

    @staticmethod
    def validate_card_number(card_number):
        return all([chr in "0123456789" for chr in card_number]) and len(card_number) == 10

    @staticmethod
    def validate_pin(pin):
        return all([chr in "0123456789" for chr in pin]) and len(pin) == 4

    def add_bank_details(self, bank_name, card_number, pin):

        valid_card_number = self.validate_card_number(card_number)
        valid_pin = self.validate_pin(pin)

        if valid_card_number and valid_pin:
            self.bank_details = BankDetails(
                self.username, bank_name, card_number, pin)
            return self.bank_details

    def checkout(self, pin):
        return pin == self.bank_details.pin


class Admin(User):

    def __init__(self) -> None:
        super().__init__("admin", "shopping123", "Admin",
                         "CIS Department, NED University, Karachi.")
