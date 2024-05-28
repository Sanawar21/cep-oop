"""
Database handler for this project.
"""

from models.cart import Cart
from models.product import Product
from models.user import User

SEP = "@#$%"


def get_products() -> "list[Product]":
    """
    Returns a list of products stored in the database as Product objects.
    """

    products = []

    with open("database/products.txt") as file:
        lines = file.readlines()
        for line in lines:
            attrs = line.strip().split(SEP)
            products.append(
                Product(attrs[0], int(float(attrs[1])), uid=attrs[2]))

    return products


def save_products(products: "list[Product]"):
    """
    Writes the products list provided to the database.
    """

    with open("database/products.txt", "a") as file:
        file.writelines([
            f"{product.title}{SEP}{product.price}{SEP}{product.uid}\n"
            for product in products
        ])


def get_users() -> "list[User]":
    """
    Returns a list of users stored in the database as User objects.
    """
    users = []
    with open("database/users.txt") as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip()
            attrs = line.split(SEP)
            users.append(
                User(attrs[0], attrs[1], attrs[2], attrs[3])
            )
    return users


def save_user(user: User):
    """
    Saves a (new) User object to database. 
    """
    with open("database/users.txt", "a") as file:
        file.write(
            f"{user.username}{SEP}{user.password}{SEP}{user.full_name}{SEP}{user.address}\n")


def remove_product_inventory(product_title: str):
    """this function reads the old file remove the product and writes the new file,
    it takes Product.title as a parameter"""

    with open("database/products.txt") as file:
        lines = file.readlines()
        new_lines = []
        for line in lines:
            if line in lines:
                if not line.startswith(f"{product_title}{SEP}"):
                    new_lines.append(line)
        with open("database/products.txt", "w") as file_:
            file_.writelines(new_lines)


def change_price(product_title: str, new_price: int):
    """this functions reads the old file access the product and change its price and writes new file and it takes """

    with open("database/products.txt") as file:
        lines = file.readlines()
        new_lines = []
        for line in lines:
            if line.startswith(f"{product_title}{SEP}"):
                new_line = f"{product_title}{SEP}{new_price}\n"
                new_lines.append(new_line)
            else:
                new_lines.append(line)
        with open("database/products.txt", "w") as file_:
            file_.writelines(new_lines)


def write_cart(user: User, cart: Cart):
    """writes the order of the user in the file of his name"""
    with open(f"database/order_histories/{user.username}", "a") as file:
        file.write(str(cart.to_dict())+"\n")


def read_carts(user: User) -> list[Cart]:
    """Returns the checked-out carts affiliated with the user.
    """
    carts: list[Cart] = []
    try:
        with open(f"database/order_histories/{user.username}") as file:
            lines = file.readlines()
            for line in lines:
                if line != "" or line != "\n":
                    cart = Cart("")  # create a blank cart
                    cart.from_dict(eval(line.strip()))
                    carts.append(cart)
    except FileNotFoundError:
        pass
    return carts
