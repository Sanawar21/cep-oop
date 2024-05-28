import time
from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash
from src.authenticate import Authenticator
from src.database import Database
from models.cart import Cart
from models.product import Product
from models.user import User
from src import routines
app = Flask(__name__)
app.secret_key = "pIQ89naMqA21"
# Initialize global variables
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
            flash('Invalid username or password.', 'error')
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


@app.route('/product_detail/<int:product_id>', methods=['GET', 'POST'])
def product_detail(product_id):
    if not user:
        flash('Please log in to view product details.', 'error')
        return redirect(url_for('login', next=request.url))

    product = all_products[product_id]
    if request.method == 'POST':
        # Handle the form submission here
        # For example, add the product to the cart or remove it
        # You may need to update the cart and then redirect to the product detail page
        return redirect(url_for('product_detail', product_id=product_id))

    return render_template('product_detail.html', product=product, product_index=int(product_id), cart=cart)


@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if not user:
        flash('Please log in to add products to your cart.', 'error')
        return jsonify({'error': 'Please log in to add products to your cart.'}), 401

    product_id = int(request.form.get('product_id'))
    product = all_products[product_id]
    cart.add_product(product, 1)
    flash('Product added to cart successfully!', 'success')
    return jsonify({'success': 'Product added to cart successfully!'}), 200


@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    if not user:
        return jsonify({'error': 'Please log in to remove products from your cart.'}), 401
    product_id = int(request.form.get('product_id'))
    product = all_products[product_id]
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


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    global cart
    if not user:
        flash('Please log in to checkout.', 'error')
        return redirect(url_for('login', next=request.url))

    if request.method == 'POST':

        # request only the bank pin at checkout
        # call user.checkout(<pin inputted>)
        # user.checkout will return True if the pin is correct else it will return False

        bank_name = request.form['bank_name']
        password = request.form['password']
        if password == user.password:
            cart.bank_name = bank_name
            cart.timestamp = time.asctime()
            # Calculate total bill
            total_bill = sum(item.product.price *
                             item.quantity for item in cart.items)
            database.write_cart(user, cart)
            flash('Checkout successful! Items will be delivered in 1 to 2 working days. Total Bill: ${}'.format(
                total_bill), 'success')
            cart = Cart(None)
            return redirect(url_for('products'))
        else:
            flash('Invalid accosunt password.', 'error')
            return render_template('checkout.html', incorrect_password=True)
    return render_template('checkout.html', incorrect_password=False)


@app.route('/history')
def history():
    if not user:
        flash('Please log in to view your order history.', 'error')
        return redirect(url_for('login', next=request.url))

    carts = database.read_carts(user)
    return render_template('history.html', carts=carts[::-1])


@app.route('/bankdetails')
def bank_details():
    global user
    if request.method == "POST":
        # TODO: Implement this
        # bank_name = request.form['bank_name']
        # card_number = request.form['password']
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
