from abc import ABC, abstractmethod
from .bank_details import BankDetails


class Account(ABC):
    def __init__(self, username, password) -> None:
        self.username = username
        self.password = password

    @abstractmethod
    def to_dict():
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data):
        pass


class User(Account):
    """
    User object for handling users in the store.
    Every User has a unique username.
    """
    type = "user"

    def __init__(self, username, password, full_name, address, bank_details=None) -> None:
        super().__init__(username, password)
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
        self.bank_details = BankDetails(
            self.username, bank_name, card_number, pin)
        return self.bank_details

    def check_pin(self, pin) -> bool:
        return pin == self.bank_details.pin


class Admin(Account):

    __ALL_PRIVILEGES = [
        "ADD_USER",
        "ADD_ADMIN",
        "ADD_PRODUCT",
        "EDIT_USER",
        "EDIT_ADMIN",
        "EDIT_PRODUCT",
        "DELETE_USER",
        "DELETE_ADMIN",
        "DELETE_PRODUCT"
    ]

    type = "admin"

    def __init__(self, username, password, privileges: list[str] | set[str]) -> None:
        super().__init__(username, password)
        self.privileges = set(privileges)

    def add_privilege(self, p: str):
        if p in self.__ALL_PRIVILEGES:
            self.privileges.add(p)
        else:
            raise ValueError("Invalid privilege")

    def has_privilege(self, p: str):
        return p in self.privileges

    def remove_privilege(self, p: str):
        if p in self.privileges:
            self.privileges.remove(p)

    def to_dict(self):
        return {
            "type": self.type,
            "username": self.username,
            "password": self.password,
            "privileges": list(self.privileges),
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["username"],
            data["password"],
            data["privileges"],
        )
