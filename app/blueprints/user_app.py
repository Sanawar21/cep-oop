from .base_app import BaseApp
from ..utils import Paths as paths

from ..models.cart import Cart
from ..models.account import User

from flask import request, render_template, jsonify


# TODO: Fix add to cart and remove from cart buttons on product detail page @talha.
# TODO: Remove view product button, instead click on the card itself.
# TODO: Use back arrow button in top left of the container instead of text button for back to products
# TODO: Do not use text buttons in product detail for back to products and add to / remove from cart
# TODO: Remove log out button from cart display page, and do not use text buttons there as well
# TODO: Remove log out from order history page.
# TODO: Look at other websites for inspiration for text buttons.
# TODO: Fix form ui design bug in checkout, form has not margin
# TODO: Fix bug, products not showing up in order history.

class UserApp(BaseApp):
    def __init__(self, user: User):
        super().__init__(
            user,
            "user",
            __name__,
            paths.templates,
            [User],
            # not working; changes made in html template paths instead
            statics=paths.static + "/.."
        )
        self.cart_ = Cart(self.database.generate_uid())

    def add_routes(self):

        all_routes = [
            self.products,
            self.cart,
            self.history,
            self.product_detail,
            self.add_to_cart,
            self.remove_from_cart,
        ]

        for route in all_routes:
            self.register_route(route)

    def products(self):
        query = request.args.get('query')
        page = int(request.args.get('page', 1))
        per_page = 12
        products = self.database.get_products()
        filtered_products = products[:]

        if query:
            filtered_products = [
                p for p in products if query.lower() in p.title.lower()]

            filtered_products = [
                p for p in products if query.lower() in p.title.lower()]

        total_pages = (len(filtered_products) + per_page - 1) // per_page
        paginated_products = filtered_products[(
            page - 1) * per_page:page * per_page]

        start_page = max(1, page - 2)
        end_page = min(start_page + 4, total_pages)

        return render_template('./store/products.html', products=paginated_products, page=page, total_pages=total_pages, start_page=start_page, end_page=end_page, max=max, min=min, new_arrivals_list=products[-6:][::-1], query=query)

    def cart(self):
        return render_template('./store/cart.html', products=self.database.get_products(), cart=self.cart_)

    def history(self):
        orders = self.database.read_orders(self.account.uid)
        return render_template('./store/history.html', orders=orders[::-1])

    def product_detail(self, product_id):
        product = self.database.get_product(product_id)
        in_cart = product in self.cart_.items
        return render_template('./store/product_detail.html', product=product, in_cart=in_cart)

    def add_to_cart(self):
        product_uid = request.form.get('product_id')
        product = self.database.get_product(product_uid)
        self.cart_.add_product(product, 1)
        return jsonify({'success': 'Product added to cart successfully!'}), 200

    def remove_from_cart(self):
        product_uid = request.form.get('product_id')
        product = self.database.get_product(product_uid)
        self.cart_.remove_product(product, 1)
        return jsonify({'success': 'Product removed from cart successfully!'}), 200
