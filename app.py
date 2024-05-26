import time
from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash
from src import authenticate, database
from models.cart import Cart
from models.product import Product
from models.user import User
from src import routines
app = Flask(__name__)
app.secret_key = 'your_secret_key'
# Initialize global variables
all_products = database.get_products()
cart = Cart(None)
user = None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    global user
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = authenticate.login(username, password)
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
        password = request.form['password']
        full_name = request.form['full_name']
        address = request.form['address']
        result = authenticate.sign_up(username, password, full_name, address)
        if type(result) == tuple:
            flash(result[1], 'error')
        else:
            user = result
            cart.owner = username
            flash('Signup successful!', 'success')
            return redirect(url_for('products'))
    return render_template('signup.html')


@app.route('/products')
def products():
    if not user:
        flash('Please log in to view products.', 'error')
        return redirect(url_for('login', next=request.url))

    return render_template('products.html', products=all_products, cart=cart)


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
    if not user:
        flash('Please log in to checkout.', 'error')
        return redirect(url_for('login', next=request.url))

    if request.method == 'POST':
        bank_name = request.form['bank_name']
        password = request.form['password']
        if password == user.password:
            cart.bank_name = bank_name
            cart.timestamp = time.asctime()
            # Calculate total bill
            total_bill = sum(item.product.price *
                             item.quantity for item in cart.items)
            database.write_cart(user, cart)
            flash('Checkout successful! Items will be delivered in 1 to 2 working days. Total Bill: Rs.{}'.format(
                total_bill), 'success')
            return redirect(url_for('products'))
        else:
            flash('Invalid account password.', 'error')
    return render_template('checkout.html')


@app.route('/history')
def history():
    if not user:
        flash('Please log in to view your order history.', 'error')
        return redirect(url_for('login', next=request.url))

    carts = database.read_carts(user)
    return render_template('history.html', carts=carts)


@app.route('/logout')
def logout():
    global user, cart
    user = None
    cart = Cart(None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
