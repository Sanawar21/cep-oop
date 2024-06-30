from flask import Flask
from .blueprints.admin_app import AdminApp
from .blueprints.user_app import UserApp
from .blueprints.checkout_app import CheckoutApp
from .blueprints.authenticate_app import AuthenticationApp

from .utils import Paths as paths


class MasterApp(Flask):
    def __init__(self):
        super().__init__(__name__, static_folder=paths.static)
        self.secret_key = "beKxrYWowAlz"
        self.register_blueprint(AuthenticationApp(), url_prefix="")
        self.register_blueprint(UserApp(), url_prefix="")
        self.register_blueprint(AdminApp(), url_prefix="/admin")
        self.register_blueprint(CheckoutApp(), url_prefix="/checkout")
