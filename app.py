from flask import Flask, render_template, request, redirect, url_for, session, flash
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

    products = database.get_products()
    return render_template('products.html', products=products,cart=cart)


@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if not user:
        flash('Please log in to add products to your cart.', 'error')
        return redirect(url_for('login', next=request.url))
    all_products = database.get_products()
    product_id = int(request.form.get('product_id'))
    if 1 <= product_id <= len(all_products):
        product = all_products[product_id - 1]
        cart.add_product(product, 1)
        flash('Product added to cart successfully!', 'success')
        return redirect(url_for('products'))
    else:
        flash('Invalid product ID.', 'error')
        return redirect(url_for('products'))
    

    
    
@app.route('/cart')
def Cart():
    if not user:
        flash('Please log in to view your cart.', 'error')
        return redirect(url_for('login', next=request.url))

    if not cart.items:
        flash('Your cart is empty.', 'info')
        return redirect(url_for('products'))

    return render_template('cart.html', cart=cart)

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        user_cart = session.get('cart', None)
        username = session['username']
        user = [u for u in database.get_users() if u.username == username][0]
        if user and user_cart:
            success = routines.checkout_routine(user_cart, user)
            if success:
                session.pop('cart', None)
                flash('Checkout successful!')
                return redirect(url_for('history'))
            else:
                flash('Checkout failed.')
    return render_template('checkout.html')

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    if not user:
        flash('Please log in to remove products from your cart.', 'error')
        return redirect(url_for('login', next=request.url))
    product_id = int(request.form.get('product_id'))
    product = all_products[product_id]
    cart.remove_product(product)
    flash('Product removed from cart successfully!', 'success')
    return redirect(url_for('products'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
