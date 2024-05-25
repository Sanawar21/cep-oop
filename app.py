from flask import Flask, render_template, request, redirect, url_for, session, flash
from src import authenticate, database
from models.cart import Cart
from models.product import Product
from models.user import User
from src import routines
from src.database import get_products, save_products, remove_product_inventory, change_price

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize global variables
products = database.get_products()

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = authenticate.login(username, password)
        if user:
            session['username'] = user.username
            return redirect(url_for('products'))
        else:
            flash('Invalid username or password.')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        full_name = request.form['full_name']
        address = request.form['address']
        result = authenticate.sign_up(username, password, full_name, address)
        if type(result) == tuple:
            flash(result[1])
        else:
            session['username'] = result.username
            return redirect(url_for('products'))
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/products')
def products():
    if 'username' not in session:
        return redirect(url_for('login'))
    products = database.get_products()

    return render_template('products.html', products=products)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    product_id = int(request.form['product_id'])
    products = database.get_products()

    if 1 <= product_id <= len(products):
        product = products[product_id - 1]
        if 'cart' not in session:
            session['cart'] = Cart()
        session['cart'].add_product(product)
        return redirect(url_for('products'))
    else:
        return "Invalid product ID"
    
    
@app.route('/cart')
def cart():
    if 'username' not in session:
        return redirect(url_for('login'))
    user_cart = session.get('cart', None)
    return render_template('cart.html', cart=user_cart)

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

@app.route('/history')
def history():
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']
    user = [u for u in database.get_users() if u.username == username][0]
    carts = database.read_carts(user)
    return render_template('history.html', carts=carts)

app.secret_key = 'your_secret_key'

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            title = request.form.get('title')
            price = request.form.get('price')
            product = Product(title, int(price))
            products = get_products()
            products.append(product)
            save_products(products)
            flash('Product added successfully', 'success')
        elif action == 'remove':
            product_title = request.form.get('product_title')
            remove_product_inventory(product_title)
            flash('Product removed successfully', 'success')
        elif action == 'change_price':
            product_title = request.form.get('product_title')
            new_price = request.form.get('new_price')
            change_price(product_title, int(new_price))
            flash('Product price updated successfully', 'success')
        return redirect(url_for('admin'))
    products = get_products()
    return render_template('admin.html', products=products)


if __name__=="__main__":
    app.run(debug=True)