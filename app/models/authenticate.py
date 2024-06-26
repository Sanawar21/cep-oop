"""
authenticate.py module for user account generation and authentication.
"""

from .account import User, Admin
from .database import Database


class Authenticator:

    def __init__(self) -> None:
        self.database = Database()
        self.account: User | Admin = None

    @staticmethod
    def validate_password(password):
        """to check password if password is valid"""

        has_digit = False
        has_special = False

        if len(password) < 8:
            return False

        for char in password:
            if char.isdigit():
                has_digit = True

            if char in "!@#$%^&*()_+{}:/.,' ":
                has_special = True
        return has_digit and has_special

    @staticmethod
    def validate_username(username):
        """to check username is valid"""
        username = username.lower()
        return bool(username) and all([char in "abcdefghijklmnopqrstuvwxyz0123456789_" for char in username])

    def unique_username(self, username):
        """to check if username is unique"""
        username = username.lower()
        accounts = self.database.get_accounts()
        for account in accounts:
            if username == account.username:
                return False
        return True

    def login(self, username, password):
        """this function would compare the values"""
        username = username.lower()
        accounts = self.database.get_accounts()
        for account in accounts:
            if account.username == username and account.password == password:
                self.account = account
                return account

    def sign_up(self, username, password, full_name, address, bank_details=None):
        """if all the inputs are valid it will return a user object containing all the data of the user
        else it would return a tuple"""
        username = username.lower()

        if not self.validate_password(password):
            return 1, "The password is not valid"

        if not self.validate_username(username):
            return 0, "This Username contains a special character."

        if not self.unique_username(username):
            return 0, "This Username has been already taken "

        user = User(Database.generate_uid(), username,
                    password, full_name, address, bank_details)
        self.database.save_account(user)
        self.login(username, password)

        return self.account

    def add_admin(self, username, password, full_name, privileges):
        admin = Admin(Database.generate_uid(), username,
                      password, full_name, privileges)
        self.database.save_account(admin)
        self.account = admin
        return admin
