from ..models.authenticate import Authenticator
from ..models.database import Database
from ..models.cart import Cart
from ..models.product import Product
from ..models.product import Product
from ..models.account import User, Admin, Privilege
from ..models.bank_details import BankDetails
from ..models.order import BankOrder, CodOrder
from ..utils import only_allow, check_privilege, completion, failure, Paths as paths


from flask import Flask, Blueprint, jsonify, render_template, request, redirect, url_for, session, flash


class AdminApp(Blueprint):

    def __init__(self, admin: Admin):
        super().__init__(
            "admin",
            __name__,
            static_folder=paths.static,
            template_folder=paths.admin_templates_base,
        )
        self.database = Database()
        self.authenticator = Authenticator()
        AdminApp.admin = admin
        self.add_routes()

    def add_routes(self):

        self.add_url_rule("/", view_func=self.index)
        self.add_url_rule(
            "/add_admin", view_func=self.add_admin, methods=['GET', 'POST'])
        self.add_url_rule(
            "/edit_admin/<uid>", view_func=self.edit_admin, methods=['GET', 'POST'])
        self.add_url_rule(
            "/delete_admin/<uid>", view_func=self.delete_admin, methods=['GET', 'POST'])

    def apply_decorators(self):
        self.index = only_allow([Admin])(self.index)
        self.add_admin = only_allow([Admin])(
            check_privilege(self.admin)(self.add_admin))
        self.edit_admin = only_allow([Admin])(
            check_privilege(self.admin)(self.edit_admin))
        self.delete_admin = only_allow([Admin])(
            check_privilege(self.admin)(self.delete_admin))

    def index(self):
        admin_type = request.args.get('type')
        page = int(request.args.get('page', 1))
        per_page = 20
        # Get the search query from the request
        search_query = request.args.get('search', '')

        if admin_type == 'products':
            all_products = self.database.get_products()
            filtered_products = [
                product for product in all_products if search_query.lower() in product.title.lower()]
            total_pages = (len(filtered_products) + per_page - 1) // per_page
            start_page = max(1, page - 2)
            end_page = min(start_page + 4, total_pages)
            paginated_products = filtered_products[(
                page - 1) * per_page:page * per_page]
            return render_template("./changes/product.html", current_admin=self.admin, products=paginated_products, page=page, total_pages=total_pages, start_page=start_page, end_page=end_page, type=admin_type)
        elif admin_type == 'users':
            accounts = self.database.get_accounts()
            users = [account for account in accounts if isinstance(
                account, User) and search_query.lower() in account.username.lower()]
            total_pages = (len(users) + per_page - 1) // per_page
            start_page = max(1, page - 2)
            end_page = min(start_page + 4, total_pages)
            paginated_users = users[(page - 1) * per_page:page * per_page]
            return render_template("./changes/user.html", current_admin=self.admin, users=paginated_users, page=page, total_pages=total_pages, start_page=start_page, end_page=end_page, type=admin_type)
        elif admin_type == 'admins':
            accounts = self.database.get_accounts()
            admins = [account for account in accounts if isinstance(
                account, Admin) and search_query.lower() in account.username.lower()]
            total_pages = (len(admins) + per_page - 1) // per_page
            start_page = max(1, page - 2)
            end_page = min(start_page + 4, total_pages)
            paginated_admins = admins[(page - 1) * per_page:page * per_page]
            return render_template("./changes/admin.html", current_admin=self.admin, admins=paginated_admins, page=page, total_pages=total_pages, start_page=start_page, end_page=end_page, type=admin_type)
        else:
            return render_template("admin.html", current_admin=self.admin)

    def add_admin(self):
        template = "./admin/add/admin.html"

        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            full_name = request.form.get("full_name")
            privileges = request.form.getlist('privileges[]')

            def render_with_error(error):
                dummy_admin = Admin(None, username, password,
                                    full_name, privileges)
                return render_template(template, admin=dummy_admin, error=error)

            if not username or not password or not full_name:
                return render_with_error("All fields are required.")

            if not self.authenticator.unique_username(username):
                return render_with_error("This username is taken.")

            if not self.authenticator.validate_username(username):
                return render_with_error("Username cannot contain any special characters.")

            if not self.authenticator.validate_password(password):
                return render_with_error("Password must be atleast 8 characters with a special character and a number.")

            if not privileges:
                return render_with_error("Select at least one privilege.")

            if privileges == Privilege.ALL:
                return render_with_error("Cannot create another superadmin.")

            self.authenticator.add_admin(
                username, password, full_name, privileges)
            return completion("Admin added successfully.", url_for("admin.index", type="admins"))

        return render_template(template)

    def edit_admin(self, uid):

        template = "./admin/edit/admin.html"

        if request.method == "POST":
            username = request.form.get("username")
            full_name = request.form.get("full_name")
            privileges = request.form.getlist('privileges[]')
            old_admin = self.database.get_account(uid)
            password = old_admin.password

            def render_with_error(error):
                dummy_admin = Admin(uid, username, password,
                                    full_name, privileges)
                return render_template(template, admin=dummy_admin, error=error)

            if not username or not password or not full_name:
                return render_with_error("All fields are required.")

            if username != old_admin.username and not self.authenticator.unique_username(username):
                return render_with_error("This username is taken.")

            if not self.authenticator.validate_username(username):
                return render_with_error("Username cannot contain any special characters.")

            if not privileges:
                return render_with_error("Select at least one privilege.")

            if privileges == Privilege.ALL:
                return render_with_error("Cannot create another superadmin.")

            self.database.overwrite_account(
                Admin(uid, username, password, full_name, privileges)
            )
            return completion("Admin edited successfully.", url_for("admin.index", type="admins"))

        if uid != self.admin.uid:
            return render_template(template, admin=self.database.get_account(uid))
        else:
            return failure("Cannot edit your own account.", url_for("admin.index", type="admins"))

    def delete_admin(self, uid):
        if "superadmin" != self.database.get_account(uid).username:
            self.database.delete_account(uid)
            return completion("Admin deleted successfully.", url_for("admin.index", type="admins"))
        else:
            return failure("Cannot delete the superadmin account.", url_for("admin.index", type="admins"))
