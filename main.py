from flask import Flask
from app.models.database import Database
from app.blueprints.admin_app import AdminApp
from app.blueprints.user_app import UserApp
from app.blueprints.checkout_app import CheckoutApp

db = Database()
account = db.get_account("mDtwbk6N1rTm")  # superadmin

app = Flask(__name__)
user_app = UserApp(account)
admin_app = AdminApp(account)
checkout_app = CheckoutApp(account, user_app.cart_)

# Implement overwrite account method in baseApp and call it when user logs out
app.register_blueprint(user_app, url_prefix="")
app.register_blueprint(admin_app, url_prefix="/admin")
app.register_blueprint(checkout_app, url_prefix="/checkout")


@app.route("/logout")
def logout():
    return "LoggedOut"


# @app.route("/checkout")
# def checkout():
#     return "CheckoutOut"


app.run(debug=True)
