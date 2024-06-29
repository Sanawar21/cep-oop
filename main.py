from flask import Flask
from app.models.database import Database
from app.blueprints.admin_app import AdminApp
from app.blueprints.user_app import UserApp
from app.blueprints.checkout_app import CheckoutApp
from app.blueprints.authenticate_app import AuthenticationApp

db = Database()

app = Flask(__name__)
app.secret_key = "beKxrYWowAlz"
auth_app = AuthenticationApp()
user_app = UserApp()
admin_app = AdminApp()
checkout_app = CheckoutApp()

# Implement overwrite account method in baseApp and call it when user logs out
app.register_blueprint(user_app, url_prefix="")
app.register_blueprint(auth_app, url_prefix="")
app.register_blueprint(admin_app, url_prefix="/admin")
app.register_blueprint(checkout_app, url_prefix="/checkout")


@app.route("/logout")
def logout():
    return "LoggedOut"


# @app.route("/checkout")
# def checkout():
#     return "CheckoutOut"


app.run(debug=True)
