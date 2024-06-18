from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash
from app.models.authenticate import Authenticator
from app.models.database import Database
from app.models.cart import Cart
from app.models.product import Product
from app.models.product import Product
from app.models.account import User, Admin, Privilege
from app.models.bank_details import BankDetails
from app.models.order import BankOrder, CodOrder

import os

app = Flask(__name__)
app.secret_key = "pIQ89naMqA21"
database = Database()
authenticator = Authenticator()
all_products = database.get_products()
cart = Cart.null()
account = None

# TODO: Work on removing redundancy by creating functions that return html templates as strings and then reuse them.
# TODO: Scroll the submit button into view when a form is submitted in correctly to focus on the error.
#       use a focus.
# TODO: Save cart if user logs out before checking out.
# TODO: Encrypt database (rb, wb, ab)
# TODO: Create admin profile and user profile

# when only_allow is called like this @only_allow(Admin), it will execute and
# only then will the decorator be returned.
# The returned decorator will then modify the function
# Example:
# @only_allow(User)
# def func():
#     # do things
# The above code will evaluate to
# def func():
#     # do things
# func = only_allow(User)(func)
# only_allow(User) will return a decorator and the func will be passed as an argument to it
# func = <decorator returned by only_allow(User)>(func)
# and the above code will evaluate to
# func = <decorated func>


def only_allow(types_: list[type] | type):
    """
    Some routes are only accessible to specific account types.
    For example, only a User account can checkout, Only a privileged Admin can
    edit products list.

    This wrapper forces this functionality. It reroutes the app to the login page
    if the current account type is not the allowed account type passed in the `types_` argument.

    The programmer can also add a list of allowed types.
    """
    if type(types_) != list:
        types_ = [types_]  # Convert the types_ argument into a list

    def decorator(func):
        def wrapper(*args, **kwargs):
            global account, cart

            if type(account) not in types_:
                account = None
                cart = Cart.null()
                return redirect(url_for('login'))
            else:
                return func(*args, **kwargs)

        # This is important because flask searches endpoints with the function names.
        # So if all functions are named `wrapper`, flask cannot differentiate between routes.
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper.__module__ = func.__module__

        return wrapper
    return decorator


def check_privilege(func):
    """
    Uses the route name to determine whether the admin has the necessary privilege to 
    perform the action and then reroutes accordingly.
    """
    def wrapper(*args, **kwargs):
        route_name = func.__name__
        if route_name not in Privilege.ALL or account.has_privilege(route_name.upper()):
            return func(*args, **kwargs)
        else:
            return failure("You do not have the privilege to perform this action.", url_for("admin"))

    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    wrapper.__module__ = func.__module__

    return wrapper


def failure(action_detail, back_link):
    template = "./admin/failure.html"
    return render_template(template, action_detail=action_detail, back_link=back_link)


def completion(action_detail, back_link):
    template = "./admin/completion.html"
    return render_template(template, action_detail=action_detail, back_link=back_link)


@app.route('/add_admin', methods=["GET", "POST"])
@only_allow(Admin)
@check_privilege
def add_admin():

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

        if not authenticator.unique_username(username):
            return render_with_error("This username is taken.")

        if not authenticator.validate_username(username):
            return render_with_error("Username cannot contain any special characters.")

        if not authenticator.validate_password(password):
            return render_with_error("Password must be atleast 8 characters with a special character and a number.")

        if not privileges:
            return render_with_error("Select at least one privilege.")

        if privileges == Privilege.ALL:
            return render_with_error("Cannot create another superadmin.")

        authenticator.add_admin(username, password, full_name, privileges)
        return completion("Admin added successfully.", url_for("admin", type="admins"))

    return render_template(template)


@app.route('/add_user', methods=["GET", "POST"])
@only_allow(Admin)
@check_privilege
def add_user():

    template = "./admin/add/user.html"

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        full_name = request.form.get("full_name")
        address = request.form.get('address')

        bank_name = request.form.get("bank_name")
        card_number = request.form.get("card_number")
        pin = request.form.get("pin")

        def render_with_error(error):
            dummy_user = User(None, username, password, full_name,
                              address, BankDetails(bank_name, card_number, pin))
            return render_template(template, user=dummy_user, error=error)

        if not username or not password or not full_name or not address:
            return render_with_error("All fields are required.")

        if not authenticator.unique_username(username):
            return render_with_error("This username is taken.")

        if not authenticator.validate_username(username):
            return render_with_error("Username cannot contain any special characters.")

        if not authenticator.validate_password(password):
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

        authenticator.sign_up(username, password,
                              full_name, address, bank_details)
        return completion("User added successfully.", url_for("admin", type="users"))

    return render_template(template)


@app.route('/add_product', methods=["GET", "POST"])
@only_allow(Admin)
@check_privilege
def add_product():

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

        if title in [p.title for p in all_products]:  # title not unique
            return render_with_error("This product title has been used.")

        try:
            price = int(price)
        except ValueError:
            return render_with_error("The price must be an integer.")

        uid = Database.generate_uid()
        if image:
            if not image.filename.endswith(('png', 'jpg', 'jpeg')):
                return render_with_error("Invalid image format. Only png, jpg and jpeg is allowed.")
            else:
                image.save(f"./static/images/{uid}.jpg")

        database.save_product(Product(title, price, uid))
        return completion("Product added successfully.", url_for("admin", type="products"))

    return render_template(template)

# Delete routes


@app.route("/delete_admin/<uid>")
@only_allow(Admin)
@check_privilege
def delete_admin(uid):
    if "superadmin" != database.get_account(uid).username:
        database.delete_account(uid)
        return completion("Admin deleted successfully.", url_for("admin", type="admins"))
    else:
        return failure("Cannot delete the superadmin account.", url_for("admin", type="admins"))


@app.route("/delete_user/<uid>")
@only_allow(Admin)
@check_privilege
def delete_user(uid):
    database.delete_account(uid)
    return completion("User deleted successfully.", url_for("admin", type="users"))


@app.route("/delete_product/<uid>")
@only_allow(Admin)
@check_privilege
def delete_product(uid):
    database.delete_product(uid)
    return completion("Product deleted successfully.", url_for("admin", type="products"))


# Edit routes


@app.route("/edit_admin/<uid>", methods=["GET", "POST"])
@only_allow(Admin)
@check_privilege
def edit_admin(uid):

    template = "./admin/edit/admin.html"

    if request.method == "POST":
        username = request.form.get("username")
        full_name = request.form.get("full_name")
        privileges = request.form.getlist('privileges[]')
        old_admin = database.get_account(uid)
        password = old_admin.password

        def render_with_error(error):
            dummy_admin = Admin(uid, username, password, full_name, privileges)
            return render_template(template, admin=dummy_admin, error=error)

        if not username or not password or not full_name:
            return render_with_error("All fields are required.")

        if username != old_admin.username and not authenticator.unique_username(username):
            return render_with_error("This username is taken.")

        if not authenticator.validate_username(username):
            return render_with_error("Username cannot contain any special characters.")

        if not privileges:
            return render_with_error("Select at least one privilege.")

        if privileges == Privilege.ALL:
            return render_with_error("Cannot create another superadmin.")

        database.overwrite_account(
            Admin(uid, username, password, full_name, privileges)
        )
        return completion("Admin edited successfully.", url_for("admin", type="admins"))

    if uid != account.uid:
        return render_template(template, admin=database.get_account(uid))
    else:
        return failure("Cannot edit your own account.", url_for("admin", type="admins"))


@app.route("/edit_user/<uid>", methods=["GET", "POST"])
@only_allow(Admin)
@check_privilege
def edit_user(uid):
    template = "./admin/edit/user.html"

    if request.method == "POST":

        old_user = database.get_account(uid)

        username = request.form.get("username")
        full_name = request.form.get("full_name")
        address = request.form.get('address')

        def render_with_error(error):
            dummy_user = User(old_user.uid, username, old_user.password,
                              full_name, address, old_user.bank_details)
            return render_template(template, user=dummy_user, error=error)

        if not username or not full_name or not address:
            return render_with_error("All fields are required.")

        if username != old_user.username and not authenticator.unique_username(username):
            return render_with_error("This username is taken.")

        if not authenticator.validate_username(username):
            return render_with_error("Username cannot contain any special characters.")

        database.overwrite_account(User(
            old_user.uid, username, old_user.password, full_name, address, old_user.bank_details))
        return completion("User edited successfully.", url_for("admin", type="users"))

    return render_template(template, user=database.get_account(uid))


@app.route("/edit_product/<uid>", methods=["GET", "POST"])
@only_allow(Admin)
@check_privilege
def edit_product(uid):
    template = "./admin/edit/product.html"

    if request.method == "POST":

        old_product = database.get_product(uid)

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
        if title != old_product.title and title in [p.title for p in all_products]:
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

        database.overwrite_product(Product(title, price, uid))
        return completion("Product edited successfully.", url_for("admin", type="products"))

    return render_template(template, product=database.get_product(uid))


@app.route('/admin')
@only_allow(Admin)
def admin():
    admin_type = request.args.get('type')
    page = int(request.args.get('page', 1))
    per_page = 20
    # Get the search query from the request
    search_query = request.args.get('search', '')

    if admin_type == 'products':
        all_products = database.get_products()
        filtered_products = [
            product for product in all_products if search_query.lower() in product.title.lower()]
        total_pages = (len(filtered_products) + per_page - 1) // per_page
        start_page = max(1, page - 2)
        end_page = min(start_page + 4, total_pages)
        paginated_products = filtered_products[(
            page - 1) * per_page:page * per_page]
        return render_template("./admin/changes/product.html", current_admin=account, products=paginated_products, page=page, total_pages=total_pages, start_page=start_page, end_page=end_page, type=admin_type)
    elif admin_type == 'users':
        accounts = database.get_accounts()
        users = [account for account in accounts if isinstance(
            account, User) and search_query.lower() in account.username.lower()]
        total_pages = (len(users) + per_page - 1) // per_page
        start_page = max(1, page - 2)
        end_page = min(start_page + 4, total_pages)
        paginated_users = users[(page - 1) * per_page:page * per_page]
        return render_template("./admin/changes/user.html", current_admin=account, users=paginated_users, page=page, total_pages=total_pages, start_page=start_page, end_page=end_page, type=admin_type)
    elif admin_type == 'admins':
        accounts = database.get_accounts()
        admins = [account for account in accounts if isinstance(
            account, Admin) and search_query.lower() in account.username.lower()]
        total_pages = (len(admins) + per_page - 1) // per_page
        start_page = max(1, page - 2)
        end_page = min(start_page + 4, total_pages)
        paginated_admins = admins[(page - 1) * per_page:page * per_page]
        return render_template("./admin/changes/admin.html", current_admin=account, admins=paginated_admins, page=page, total_pages=total_pages, start_page=start_page, end_page=end_page, type=admin_type)
    else:
        return render_template("./admin/admin.html", current_admin=account)


@app.route('/')
def index():
    return render_template('./user_authentication/index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    global account
    global all_products
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        account = authenticator.login(username, password)
        if account:
            all_products = database.get_products()
            if account.type == User.type:
                return redirect(url_for('products'))
            else:
                return redirect(url_for("admin"))
        else:
            return render_template("./user_authentication/login.html", error="Incorrect username or password.")
    return render_template('./user_authentication/login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    global account
    if request.method == 'POST':
        username = request.form['username']
        session["username"] = username
        password = request.form['password']
        session["password"] = password
        full_name = request.form['full_name']
        session["full_name"] = full_name
        address = request.form['address']
        session["address"] = address

        if not username or not password or not full_name or not address:
            return render_template('./user_authentication/signup.html',
                                   error="All fields are required.",
                                   username=username,
                                   password=password,
                                   full_name=full_name,
                                   address=address)

        if not authenticator.unique_username(username):
            return render_template('./user_authentication/signup.html',
                                   error="This username is taken.",
                                   username=username,
                                   password=password,
                                   full_name=full_name,
                                   address=address)

        if not authenticator.validate_username(username):
            return render_template('./user_authentication/signup.html',
                                   error="Username cannot contain any special characters.",
                                   username=username,
                                   password=password,
                                   full_name=full_name,
                                   address=address)
        if not authenticator.validate_password(password):
            return render_template('./user_authentication/signup.html',
                                   error="Password must be atleast 8 characters with a special character and a number.",
                                   username=username,
                                   password=password,
                                   full_name=full_name,
                                   address=address)

        return redirect(url_for('bank_details'))

    return render_template('./user_authentication/signup.html')


@app.route('/products')
@only_allow(User)
def products():
    query = request.args.get('query')
    page = int(request.args.get('page', 1))
    per_page = 12
    filtered_products = all_products[:]
    products = all_products

    if query:
        filtered_products = [
            p for p in all_products if query.lower() in p.title.lower()]

        filtered_products = [
            p for p in all_products if query.lower() in p.title.lower()]

    total_pages = (len(filtered_products) + per_page - 1) // per_page
    paginated_products = filtered_products[(
        page - 1) * per_page:page * per_page]

    start_page = max(1, page - 2)
    end_page = min(start_page + 4, total_pages)

    return render_template('./store/products.html', products=paginated_products, page=page, total_pages=total_pages, start_page=start_page, end_page=end_page, max=max, min=min, new_arrivals_list=products[-6:][::-1], query=query)


@app.route('/product_detail/<product_id>', methods=['GET'])
@only_allow(User)
def product_detail(product_id):
    product = database.get_product(product_id)
    in_cart = product in cart.items
    return render_template('./store/product_detail.html', product=product, in_cart=in_cart)


@app.route('/add_to_cart', methods=['POST'])
@only_allow(User)
def add_to_cart():
    product_uid = request.form.get('product_id')
    product = database.get_product(product_uid)
    cart.add_product(product, 1)
    return jsonify({'success': 'Product added to cart successfully!'}), 200


@app.route('/remove_from_cart', methods=['POST'])
@only_allow(User)
def remove_from_cart():
    product_uid = request.form.get('product_id')
    product = database.get_product(product_uid)
    cart.remove_product(product, 1)
    return jsonify({'success': 'Product removed from cart successfully!'}), 200


@app.route('/cart')
@only_allow(User)
def cart_():
    return render_template('./store/cart.html', products=all_products, cart=cart)


@app.route('/checkout-cod', methods=['GET', 'POST'])
@only_allow(User)
def checkout_cod():
    global cart
    if request.method == 'POST':
        address = request.form['address']
        full_name = request.form['full_name']
        password = request.form['password']
        email = request.form['email']
        phone = request.form['phone']

        dummy_user = User(
            None,
            account.username,
            account.password,
            full_name,
            address,
            account.bank_details,
        )

        if not address or not full_name or not password or not email or not phone:
            return render_template('./checkout/checkout_cod.html',
                                   # implemented dummy account here
                                   user=dummy_user,
                                   email=email,
                                   phone=phone,
                                   password=password,
                                   error="All fields are required.")

        if password == account.password:
            order = CodOrder(Database.generate_uid(), cart,
                             full_name, address, email, phone)
            database.write_order(order, account.uid)
            cart = Cart.null()
            return render_template('./user_authentication/thankyou.html')

        else:
            return render_template('./checkout/checkout_cod.html',
                                   user=dummy_user,
                                   email=email,
                                   phone=phone,
                                   password=password,
                                   error="Incorrect account password.")

    return render_template('./checkout/checkout_cod.html', user=account)


@app.route('/checkout-bank', methods=['GET', 'POST'])
@only_allow(User)
def checkout_bank():
    global account, cart

    if request.method == "POST":

        # get details

        address = request.form["address"]
        full_name = request.form["full_name"]
        if account.bank_details:
            pin = request.form["pin"]
        else:  # bank details were passed right now
            bank_name = request.form["bank_name"]
            card_number = request.form["card_number"]
            pin = request.form["pin"]

        # for state management
        dummy_user = User(
            None,
            account.username,
            account.password,
            full_name,
            address,
            account.bank_details if account.bank_details else BankDetails(
                bank_name, card_number, pin,
            )
        )

        # check validity

        if account.bank_details:
            if not pin or not address or not full_name:
                return render_template(
                    './checkout/checkout_bank.html',
                    error="All fields are required.",
                    user=dummy_user,
                )

            if not account.check_pin(pin):
                return render_template(
                    './checkout/checkout_bank.html',
                    error="Incorrect pin.",
                    user=dummy_user,
                )
        else:
            if not bank_name or not card_number or not pin or not address or not full_name:
                return render_template(
                    "./checkout/checkout_bank.html",
                    error="All fields are required.",
                    user=dummy_user,
                )
            if not BankDetails.validate_card_number(card_number):
                return render_template(
                    "./checkout/checkout_bank.html",
                    error="Card number must be 10 digits.",
                    user=dummy_user,
                )

            if not BankDetails.validate_pin(pin):
                return render_template(
                    "./checkout/checkout_bank.html",
                    error="Pin must be 4 digit long.",
                    user=dummy_user,
                )

        if not account.bank_details:
            account.add_bank_details(bank_name, card_number, pin)
            account = database.overwrite_account(account)

        # details are valid and usable
        order = BankOrder(Database.generate_uid(), cart, account.full_name,
                          address, account.bank_details)

        database.write_order(order, account.uid)
        cart = Cart.null()
        return render_template('./user_authentication/thankyou.html')

    return render_template('./checkout/checkout_bank.html', user=account)


@app.route('/checkout', methods=['GET'])
@only_allow(User)
def checkout():
    global cart
    if account.bank_details:
        return render_template("./checkout/checkout_bank.html", user=account)
    else:
        return render_template("./checkout/checkout_cod.html", user=account)


@app.route('/history')
@only_allow(User)
def history():
    orders = database.read_orders(account.uid)
    return render_template('./store/history.html', orders=orders[::-1])


@app.route('/nobankdetails', methods=["GET", "POST"])
def no_bank_details():
    global account, cart
    result = authenticator.sign_up(
        session["username"],
        session["password"],
        session["full_name"],
        session["address"],
    )
    if type(result) == tuple:
        flash(result[1], 'error')
    else:
        account = result
        return redirect(url_for('products'))


@app.route('/bankdetails', methods=['GET', 'POST'])
def bank_details():
    global account, cart
    if request.method == "POST":
        bank_name = request.form['bank_name']
        card_number = request.form['card_number']
        pin = request.form['pin']

        if not bank_name or not card_number or not pin:
            return render_template(
                "./user_authentication/bank_details.html",
                error="All fields are required.",
                bank_name=bank_name,
                card_number=card_number,
                pin=pin,
            )
        if not User.validate_card_number(card_number):
            return render_template(
                "./user_authentication/bank_details.html",
                error="Card number must be 10 digits.",
                bank_name=bank_name,
                card_number=card_number,
                pin=pin,
            )

        if not User.validate_pin(pin):
            return render_template(
                "./user_authentication/bank_details.html",
                error="Pin must be 4 digit long.",
                bank_name=bank_name,
                card_number=card_number,
                pin=pin,
            )

        bank = BankDetails(bank_name, card_number, pin)
        result = authenticator.sign_up(
            session["username"],
            session["password"],
            session["full_name"],
            session["address"],
            bank
        )

        if type(result) == tuple:
            flash(result[1], 'error')
        else:
            account = result
            return redirect(url_for('products'))

    return render_template("./user_authentication/bank_details.html")


@app.route('/logout')
@only_allow([User, Admin])
def logout():
    global account, cart
    account = None
    cart = Cart.null()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
