from flask import Flask
from app.models.database import Database
from app.blueprints.admin_app import AdminApp

db = Database()
admin = db.get_account("3")  # superadmin

app = Flask(__name__)
app.register_blueprint(AdminApp(admin), url_prefix="/admin")


@app.route("/logout")
def logout():
    return "LoggedOut"


app.run(debug=True)
