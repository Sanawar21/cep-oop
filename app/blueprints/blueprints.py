from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash
from models.authenticate import Authenticator
from models.database import Database
from models.cart import Cart
from models.product import Product
from models.product import Product
from models.account import User, Admin, Privilege
from models.bank_details import BankDetails
from models.order import BankOrder, CodOrder

import os


class AdminApp(Flask):
    pass


class UserApp(Flask):
    pass


class MasterApp(Flask):
    def __init__(self):
        super().__init__(__name__)
        self.admin_app = AdminApp()
        self.user_app = UserApp
