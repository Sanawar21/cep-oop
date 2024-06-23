from flask import Flask
from app.models.database import Database
from app.blueprints.admin_app import AdminApp
from app.blueprints.user_app import UserApp

db = Database()
account = db.get_account("mDtwbk6N1rTm")  # superadmin

app = Flask(__name__)
# Implement overwrite account method in baseApp and call it when user logs out
app.register_blueprint(UserApp(account), url_prefix="")
app.register_blueprint(AdminApp(account), url_prefix="/admin")


@app.route("/logout")
def logout():
    return "LoggedOut"


@app.route("/checkout")
def checkout():
    return "CheckoutOut"


app.run(debug=True)
