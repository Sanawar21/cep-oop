from ..models.account import User
from ..utils import Paths as paths
from ..models.bank_details import BankDetails
from .base_app import BaseApp

from flask import render_template, redirect, request, url_for, session


class AuthenticationApp(BaseApp):
    def __init__(self):
        super().__init__(
            "authenticate",
            __name__,
            paths.templates,
            allowed_types=[type]
        )

    def add_routes(self):
        self.add_url_rule("/", view_func=self.index,
                          methods=self.allowed_methods)
        self.add_url_rule("/login", view_func=self.login,
                          methods=self.allowed_methods)
        self.add_url_rule("/signup", view_func=self.signup,
                          methods=self.allowed_methods)
        self.add_url_rule("/logout", view_func=self.logout,
                          methods=self.allowed_methods)
        self.add_url_rule(
            "/nobankdetails", view_func=self.nobankdetails, methods=self.allowed_methods)
        self.add_url_rule(
            "/bankdetails", view_func=self.bankdetails, methods=self.allowed_methods)

    def index(self):
        return render_template('./user_authentication/index.html')

    def login(self):
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            self.account = self.authenticator.login(username, password)
            if self.account:
                session["cart"] = None
                if self.account.type == User.type:
                    return redirect(url_for('user.products'))
                else:
                    return redirect(url_for("admin.index"))
            else:
                return render_template("./user_authentication/login.html", error="Incorrect username or password.")
        return render_template('./user_authentication/login.html')

    def logout(self):
        session["cart"] = None
        self.account = None
        return self.index()

    def signup(self):
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            full_name = request.form['full_name']
            address = request.form['address']

            # For using later
            session["username"] = username
            session["password"] = password
            session["full_name"] = full_name
            session["address"] = address

            if not username or not password or not full_name or not address:
                return render_template('./user_authentication/signup.html',
                                       error="All fields are required.",
                                       username=username,
                                       password=password,
                                       full_name=full_name,
                                       address=address)

            if not self.authenticator.unique_username(username):
                return render_template('./user_authentication/signup.html',
                                       error="This username is taken.",
                                       username=username,
                                       password=password,
                                       full_name=full_name,
                                       address=address)

            if not self.authenticator.validate_username(username):
                return render_template('./user_authentication/signup.html',
                                       error="Username cannot contain any special characters.",
                                       username=username,
                                       password=password,
                                       full_name=full_name,
                                       address=address)
            if not self.authenticator.validate_password(password):
                return render_template('./user_authentication/signup.html',
                                       error="Password must be atleast 8 characters with a special character and a number.",
                                       username=username,
                                       password=password,
                                       full_name=full_name,
                                       address=address)

            return redirect(url_for('authenticate.bankdetails'))

        return render_template('./user_authentication/signup.html')

    def bankdetails(self):
        if request.method == "POST":
            bank_name = request.form['bank_name']
            card_number = request.form['card_number']
            pin = request.form['pin']

            if not bank_name or not card_number or not pin:
                return render_template(
                    "./user_authentication/bank_details.html",
                    error="All fields are required.",
                    bank_name=bank_name,
                    card_number=card_number,
                    pin=pin,
                )
            if not User.validate_card_number(card_number):
                return render_template(
                    "./user_authentication/bank_details.html",
                    error="Card number must be 10 digits.",
                    bank_name=bank_name,
                    card_number=card_number,
                    pin=pin,
                )

            if not User.validate_pin(pin):
                return render_template(
                    "./user_authentication/bank_details.html",
                    error="Pin must be 4 digit long.",
                    bank_name=bank_name,
                    card_number=card_number,
                    pin=pin,
                )

            bank = BankDetails(bank_name, card_number, pin)
            result = self.authenticator.sign_up(
                session["username"],
                session["password"],
                session["full_name"],
                session["address"],
                bank
            )
            assert type(result) == User
            self.account = result
            session["cart"] = None
            return redirect(url_for('user.products'))

        return render_template("./user_authentication/bank_details.html")

    def nobankdetails(self):
        result = self.authenticator.sign_up(
            session["username"],
            session["password"],
            session["full_name"],
            session["address"],
        )
        assert type(result) == User
        self.account = result

        # remove unnecessary data from session
        del session["username"]
        del session["password"]
        del session["full_name"]
        del session["address"]
        session["cart"] = None

        return redirect(url_for('user.products'))
