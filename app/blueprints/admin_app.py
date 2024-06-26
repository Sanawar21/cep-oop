from ..models.product import Product
from ..models.account import User, Admin, Privilege
from ..models.bank_details import BankDetails
from ..utils import completion, failure, Paths as paths
from .base_app import BaseApp

import os

from flask import render_template, request, url_for


class AdminApp(BaseApp):

    def __init__(self):
        super().__init__(
            "admin",
            __name__,
            paths.admin_templates_base,
            [Admin],
        )

    def add_routes(self):
        # self.index = only_allow(self.account, [Admin])(self.index)
        self.add_url_rule("/", view_func=self.index)

        all_routes = [
            self.add_admin,
            self.edit_admin,
            self.delete_admin,
            self.add_user,
            self.edit_user,
            self.delete_user,
            self.add_product,
            self.edit_product,
            self.delete_product,
        ]

        for route in all_routes:
            self.register_route(route)

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
            return render_template("./changes/product.html", current_admin=self.account, products=paginated_products, page=page, total_pages=total_pages, start_page=start_page, end_page=end_page, type=admin_type)
        elif admin_type == 'users':
            accounts = self.database.get_accounts()
            users = [account for account in accounts if isinstance(
                account, User) and search_query.lower() in account.username.lower()]
            total_pages = (len(users) + per_page - 1) // per_page
            start_page = max(1, page - 2)
            end_page = min(start_page + 4, total_pages)
            paginated_users = users[(page - 1) * per_page:page * per_page]
            return render_template("./changes/user.html", current_admin=self.account, users=paginated_users, page=page, total_pages=total_pages, start_page=start_page, end_page=end_page, type=admin_type)
        elif admin_type == 'admins':
            accounts = self.database.get_accounts()
            admins = [account for account in accounts if isinstance(
                account, Admin) and search_query.lower() in account.username.lower()]
            total_pages = (len(admins) + per_page - 1) // per_page
            start_page = max(1, page - 2)
            end_page = min(start_page + 4, total_pages)
            paginated_admins = admins[(page - 1) * per_page:page * per_page]
            return render_template("./changes/admin.html", current_admin=self.account, admins=paginated_admins, page=page, total_pages=total_pages, start_page=start_page, end_page=end_page, type=admin_type)
        else:
            return render_template("admin.html", current_admin=self.account)

    def add_admin(self):
        template = "./admin/add/admin.html"

        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            full_name = request.form.get("full_name")
            privileges = request.form.getlist('privileges[]')

            if username:
                username = username.lower()

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

        if uid != self.account.uid:
            return render_template(template, admin=self.database.get_account(uid))
        else:
            return failure("Cannot edit your own account.", url_for("admin.index", type="admins"))

    def delete_admin(self, uid):
        if "superadmin" != self.database.get_account(uid).username:
            self.database.delete_account(uid)
            return completion("Admin deleted successfully.", url_for("admin.index", type="admins"))
        else:
            return failure("Cannot delete the superadmin account.", url_for("admin.index", type="admins"))

    def add_user(self):
        template = "./admin/add/user.html"

        if request.method == "POST":

            username = request.form.get("username")
            password = request.form.get("password")
            full_name = request.form.get("full_name")
            address = request.form.get('address')

            if username:
                username = username.lower()

            bank_name = request.form.get("bank_name")
            card_number = request.form.get("card_number")
            pin = request.form.get("pin")

            def render_with_error(error):
                dummy_user = User(None, username, password, full_name,
                                  address, BankDetails(bank_name, card_number, pin))
                return render_template(template, user=dummy_user, error=error)

            if not username or not password or not full_name or not address:
                return render_with_error("All fields are required.")

            if not self.authenticator.unique_username(username):
                return render_with_error("This username is taken.")

            if not self.authenticator.validate_username(username):
                return render_with_error("Username cannot contain any special characters.")

            if not self.authenticator.validate_password(password):
                return render_with_error("Password must be atleast 8 characters with a special character and a number.")

            # handle bank details
            bank_details = None

            if card_number and bank_name and pin:
                if not BankDetails.validate_card_number(card_number):
                    return render_with_error("Card number must be 10 digits.")
                if not BankDetails.validate_pin(pin):
                    return render_with_error("Pin must be 4 digit long.")
                bank_details = BankDetails(bank_name, card_number, pin)
            else:
                if card_number or bank_name or pin:
                    return render_with_error("All bank details should be filled or left empty.")

            self.authenticator.sign_up(username, password,
                                       full_name, address, bank_details)
            return completion("User added successfully.", url_for("admin.index", type="users"))

        return render_template(template)

    def edit_user(self, uid):
        template = "./admin/edit/user.html"

        if request.method == "POST":

            old_user = self.database.get_account(uid)

            username = request.form.get("username")
            full_name = request.form.get("full_name")
            address = request.form.get('address')

            def render_with_error(error):
                dummy_user = User(old_user.uid, username, old_user.password,
                                  full_name, address, old_user.bank_details)
                return render_template(template, user=dummy_user, error=error)

            if not username or not full_name or not address:
                return render_with_error("All fields are required.")

            if username != old_user.username and not self.authenticator.unique_username(username):
                return render_with_error("This username is taken.")

            if not self.authenticator.validate_username(username):
                return render_with_error("Username cannot contain any special characters.")

            self.database.overwrite_account(User(
                old_user.uid, username, old_user.password, full_name, address, old_user.bank_details))
            return completion("User edited successfully.", url_for("admin.index", type="users"))

        return render_template(template, user=self.database.get_account(uid))

    def delete_user(self, uid):
        self.database.delete_account(uid)
        return completion("User deleted successfully.", url_for("admin.index", type="users"))

    def add_product(self):
        template = "./admin/add/product.html"

        if request.method == "POST":
            title = request.form.get("title")
            price = request.form.get("price")
            image = request.files.get("image")

            # for state management
            def render_with_error(error):
                return render_template(template, product=Product(title, price, None), error=error)

            if not title or not price:
                return render_with_error("All fields are required.")

            if title in [p.title for p in self.database.get_products()]:  # title not unique
                return render_with_error("This product title has been used.")

            try:
                price = int(price)
            except ValueError:
                return render_with_error("The price must be an integer.")

            uid = self.database.generate_uid()
            if image:
                if not image.filename.endswith(('png', 'jpg', 'jpeg')):
                    return render_with_error("Invalid image format. Only png, jpg and jpeg is allowed.")
                else:
                    image.save(f"./static/images/{uid}.jpg")

            self.database.save_product(Product(title, price, uid))
            return completion("Product added successfully.", url_for("admin.index", type="products"))

        return render_template(template)

    def edit_product(self, uid):
        template = "./admin/edit/product.html"

        if request.method == "POST":

            old_product = self.database.get_product(uid)

            title = request.form.get("title")
            price = request.form.get("price")
            image = request.files.get("image")
            image_choice = request.form.get("image_choice")

            # for state management
            def render_with_error(error):
                return render_template(template, product=Product(title, price, uid), error=error)

            if not title or not price:
                return render_with_error("All fields are required.")

            # title not unique
            if title != old_product.title and title in [p.title for p in self.database.get_products()]:
                return render_with_error("This product title has been used.")

            try:
                price = int(price)
            except ValueError:
                return render_with_error("The price must be an integer.")

            # if there is an image in the form, overwrite the existing product image
            # if the user wants to remove the image, delete the existing image
            # if he wants to keep it, pass

            if image:
                if not image.filename.endswith(('png', 'jpg', 'jpeg')):
                    return render_with_error("Invalid image format. Only png, jpg and jpeg is allowed.")
                else:
                    image.save(f"./static/images/{uid}.jpg")
            else:
                if image_choice == "remove":
                    try:
                        os.remove(f"./static/images/{uid}.jpg")
                    except FileNotFoundError:
                        pass
                else:
                    pass

            self.database.overwrite_product(Product(title, price, uid))
            return completion("Product edited successfully.", url_for("admin.index", type="products"))

        return render_template(template, product=self.database.get_product(uid))

    def delete_product(self, uid):
        self.database.delete_product(uid)
        return completion("Product deleted successfully.", url_for("admin.index", type="products"))
