from app.models.account import User
from app.utils import Paths as paths
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
        # self.add_url_rule("/nobankdetails", view_func=self.nobankdetails, methods=self.allowed_methods)
        # self.add_url_rule("/bankdetails", view_func=self.bankdetails, methods=self.allowed_methods)

    def index(self):
        return render_template('./user_authentication/index.html')

    def login(self):
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            self.account = self.authenticator.login(username, password)
            if self.account:
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
