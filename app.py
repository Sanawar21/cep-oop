import time
from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash
from src.authenticate import Authenticator
from src.database import Database
from models.cart import Cart
from models.user import User, BankDetails
from models.order import BankOrder, CodOrder

app = Flask(__name__)
app.secret_key = "pIQ89naMqA21"
database = Database()
authenticator = Authenticator()
all_products = database.get_products()
cart = Cart.null()
user = None

# TODO: 1) Tell user when the infos are invalid or incorrect and display appropriate message
#       at login and signup and checkout
#       2) User can save carts without checking out (Operator overloading { Cart + Cart })


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    global user
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = authenticator.login(username, password)
        if user:
            cart.owner = user.username
            flash('Login successful!', 'success')
            return redirect(url_for('products'))
        else:
            return render_template("login.html", error="Invalid username or password.")
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    global user
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
            return render_template('signup.html',
                                   error="All fields are required.",
                                   username=username,
                                   password=password,
                                   full_name=full_name,
                                   address=address)

        if not authenticator.unique_username(username):
            return render_template('signup.html',
                                   error="This username is taken.",
                                   username=username,
                                   password=password,
                                   full_name=full_name,
                                   address=address)

        if not authenticator.validate_username(username):
            return render_template('signup.html',
                                   error="Username cannot contain any special characters.",
                                   username=username,
                                   password=password,
                                   full_name=full_name,
                                   address=address)
        if not authenticator.validate_password(password):
            return render_template('signup.html',
                                   error="Password must be atleast 8 characters with a special character and a number.",
                                   username=username,
                                   password=password,
                                   full_name=full_name,
                                   address=address)

        return redirect(url_for('bank_details'))

    return render_template('signup.html')


@app.route('/products')
def products():
    if not user:
        flash('Please log in to view products.', 'error')
        return redirect(url_for('login', next=request.url))

    return render_template('products.html', products=all_products, cart=cart)


@app.route('/product_detail/<product_id>', methods=['GET'])
def product_detail(product_id):
    if not user:
        flash('Please log in to view product details.', 'error')
        return redirect(url_for('login', next=request.url))

    product = database.get_product(product_id)
    in_cart = product in cart.items
    return render_template('product_detail.html', product=product, in_cart=in_cart)


@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if not user:
        flash('Please log in to add products to your cart.', 'error')
        return jsonify({'error': 'Please log in to add products to your cart.'}), 401

    product_uid = request.form.get('product_id')
    product = database.get_product(product_uid)
    cart.add_product(product, 1)
    return jsonify({'success': 'Product added to cart successfully!'}), 200


@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    if not user:
        return jsonify({'error': 'Please log in to remove products from your cart.'}), 401

    product_uid = request.form.get('product_id')
    product = database.get_product(product_uid)
    cart.remove_product(product, 1)
    return jsonify({'success': 'Product removed from cart successfully!'}), 200


@app.route('/cart')
def cart_():
    if not user:
        flash('Please log in to view your cart.', 'error')
        return redirect(url_for('login', next=request.url))

    # if not cart.items:
    #     flash('Your cart is empty.', 'info')
    #     return redirect(url_for('products'))

    return render_template('cart.html', products=all_products, cart=cart)


@app.route('/checkout-cod', methods=['GET', 'POST'])
def checkout_cod():
    global cart

    if not user:
        return redirect(url_for('login', next=request.url))

    if request.method == 'POST':
        address = request.form['address']
        full_name = request.form['full_name']
        password = request.form['password']
        email = request.form['email']
        phone = request.form['phone']

        dummy_user = User(
            user.username,
            user.password,
            full_name,
            address,
            user.bank_details,
        )

        if not address or not full_name or not password or not email or not phone:
            return render_template('checkout_cod.html',
                                   # implemented dummy user here
                                   user=dummy_user,
                                   email=email,
                                   phone=phone,
                                   password=password,
                                   error="All fields are required.")

        if password == user.password:
            order = CodOrder(cart, full_name, address, email, phone)
            database.write_order(order)

            cart = Cart.null()
            return render_template('thankyou.html')
        else:
            return render_template('checkout_cod.html',
                                   user=dummy_user,
                                   email=email,
                                   phone=phone,
                                   password=password,
                                   error="Incorrect account password.")

    return render_template('checkout_cod.html', user=user)


@app.route('/checkout-bank', methods=['GET', 'POST'])
def checkout_bank():
    global user, cart

    if request.method == "POST":

        # get details

        address = request.form["address"]
        full_name = request.form["full_name"]
        if user.bank_details:
            pin = request.form["pin"]
        else:  # bank details were passed right now
            bank_name = request.form["bank_name"]
            card_number = request.form["card_number"]
            pin = request.form["pin"]

        dummy_user = User(
            user.username,
            user.password,
            full_name,
            address,
            user.bank_details if user.bank_details else BankDetails(
                user.username, bank_name, card_number, pin,
            )
        )

        # check validity

        if user.bank_details:
            if not pin or not address or not full_name:
                return render_template(
                    'checkout_bank.html',
                    error="All fields are required.",
                    user=dummy_user,
                )

            if not user.check_pin(pin):
                return render_template(
                    'checkout_bank.html',
                    error="Incorrect pin.",
                    user=dummy_user,
                )
        else:
            if not bank_name or not card_number or not pin or not address or not full_name:
                return render_template(
                    "checkout_bank.html",
                    error="All fields are required.",
                    user=dummy_user,
                )
            if not BankDetails.validate_card_number(card_number):
                return render_template(
                    "checkout_bank.html",
                    error="Card number must be 10 digits.",
                    user=dummy_user,
                )

            if not BankDetails.validate_pin(pin):
                return render_template(
                    "checkout_bank.html",
                    error="Pin must be 4 digit long.",
                    user=dummy_user,
                )

        if not user.bank_details:
            user.add_bank_details(bank_name, card_number, pin)
            user = database.overwrite_user(user)

        # details are valid and usable
        order = BankOrder(cart, user.full_name, address, user.bank_details)

        database.write_order(order)
        cart = Cart.null()

        return render_template('thankyou.html')

    # TODO: Decide what info should be passed to checkout_bank.html
    # Maybe a dummy user will work
    return render_template('checkout_bank.html', user=user)


@app.route('/checkout', methods=['GET'])
def checkout():
    global cart
    if not user:
        flash('Please log in to checkout.', 'error')
        return redirect(url_for('login', next=request.url))

    if user.bank_details:
        return render_template("checkout_bank.html", user=user)
    else:
        return render_template("checkout_cod.html", user=user)


@app.route('/history')
def history():
    if not user:
        flash('Please log in to view your order history.', 'error')
        return redirect(url_for('login', next=request.url))

    orders = database.read_orders(user.username)
    return render_template('history.html', orders=orders[::-1])


@app.route('/nobankdetails', methods=["GET", "POST"])
def no_bank_details():
    global user
    result = authenticator.sign_up(
        session["username"],
        session["password"],
        session["full_name"],
        session["address"],
    )
    if type(result) == tuple:
        flash(result[1], 'error')
    else:
        user = result
        cart.owner = user.username
        return redirect(url_for('products'))


@app.route('/bankdetails', methods=['GET', 'POST'])
def bank_details():
    global user
    if request.method == "POST":
        bank_name = request.form['bank_name']
        card_number = request.form['card_number']
        pin = request.form['pin']

        if not bank_name or not card_number or not pin:
            return render_template(
                "bank_details.html",
                error="All fields are required.",
                bank_name=bank_name,
                card_number=card_number,
                pin=pin,
            )
        if not User.validate_card_number(card_number):
            return render_template(
                "bank_details.html",
                error="Card number must be 10 digits.",
                bank_name=bank_name,
                card_number=card_number,
                pin=pin,
            )

        if not User.validate_pin(pin):
            return render_template(
                "bank_details.html",
                error="Pin must be 4 digit long.",
                bank_name=bank_name,
                card_number=card_number,
                pin=pin,
            )

        bank = BankDetails(session["username"], bank_name, card_number, pin)
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
            user = result
            cart.owner = user.username
            return redirect(url_for('products'))

    return render_template("bank_details.html")


@app.route('/logout')
def logout():
    global user, cart
    user = None
    cart = Cart.null()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
