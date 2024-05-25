"""
authenticate.py module for user account generation and authentication.
"""

from models.user import User
from src.database import get_users, save_user


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


def validate_username(username):
    """to check username is valid"""
    for char in username:
        if char in "!@#$%^&*()_+{}:/.,' ":
            return False
    return True


def unique_username(username):
    """to check if username is unique"""
    users = get_users()
    for user in users:
        if username == user.username:
            return False
    return True


def login(username, password):
    """this function would compare the values"""
    users = get_users()
    for user in users:
        if user.username == username and user.password == password:
            return user
    return None


def sign_up(username, password, full_name, address):
    """if all the inputs are valid it will return a user object containing all the data of the user
       else it would return a tuple"""
    if validate_password(password):
        pass
    else:
        return 1, "The password is not valid"

    if not validate_username(username):
        return 0, "This Username contains a special character."
    if not unique_username(username):
        return 0, "This Username has been already taken "
    user = User(username, password, full_name, address)
    save_user(user)
    return user


def admin_login(password):
    """password for admin is shopping123"""
    if password == "shopping123":
        return True
    else:
        return False
