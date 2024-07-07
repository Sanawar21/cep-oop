from flask import Flask, render_template
from .blueprints.admin_app import AdminApp
from .blueprints.user_app import UserApp
from .blueprints.checkout_app import CheckoutApp
from .blueprints.authenticate_app import AuthenticationApp

from .utils import Paths as paths


class MasterApp(Flask):
    def __init__(self):
        super().__init__(__name__, static_folder=paths.static, template_folder=paths.templates)
        self.secret_key = "beKxrYWowAlz"
        self.register_blueprint(AuthenticationApp(), url_prefix="")
        self.register_blueprint(UserApp(), url_prefix="")
        self.register_blueprint(AdminApp(), url_prefix="/admin")
        self.register_blueprint(CheckoutApp(), url_prefix="/checkout")
        self.register_error_handler(404, self.page_not_found)

    def page_not_found(self):
        return render_template("./user_authentication/error404.html")
