from src import authenticate, database
from models.product import Product
from models.cart import Cart
from models.user import User
import time


def admin_login_routine():
    """
    Ask for admin user detail if they are right then returns True else return False
    """

    password = input("Enter Admin Password:")
    if authenticate.admin_login(password):
        return True
    else:
        print("Incorrect admin ID")
        continue_ = input("To continue press y:").lower()
        if continue_ == "y":
            return admin_login_routine()  # used a recursive function
        else:
            return False


def login_routine():
    """
    Login routine for better code management.
    Keeps asking user for login details incase they are incorrect.
    returns: None if the user wants to quit
             User object if the successful login. 
    """
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    result = authenticate.login(username, password)

    if result != None:
        return result
    else:
        print("Incorrect password.")
        if 'y' == input("Do you wish to try again? (y/n) ").lower():
            print()
            return login_routine()  # implemented recursive function instead of while loop
        else:
            return None


def sign_up_routine():
    """
    Sign up routine for better code management.
    Keeps asking user for sign up details incase they are incorrect.
    returns: None if the user wants to quit
             User object if the successful sign up. 
    """

    username = input(
        "Enter username (cannot contain spaces or special characters): ")
    password = input(
        "Enter password (must be greater than 8 character, contain a special character and a digit): ")
    full_name = input("Enter full name: ")
    address = input("Enter address: ")
    print()
    result = authenticate.sign_up(username, password, full_name, address)

    while True:
        if type(result) != tuple:  # check if it returned a User object

            return result

        else:  # There was a problem with the values user entered in this case.

            while type(result) == tuple:  # keep repeating until there are valid values
                code = result[0]
                message = result[1]

                print(message)

                # check if the user wants to continue or quit
                if 'y' == input("Do you wish to try again? (y/n) ").lower():
                    if code == 0:
                        username = input("Enter username again: ")
                    elif code == 1:
                        password = input("Enter password again: ")
                    elif code == 2:
                        full_name = input("Enter full name again: ")
                    elif code == 3:
                        address = input("Enter address again: ")
                    # overwrite result variable
                    print()
                    result = authenticate.sign_up(
                        username, password, full_name, address)

                else:
                    return None  # user does not want to continue

            # This code will only be executed if user wanted to continue and entered valid corrected detail(s).
            else:
                return result


def __pad(string, padding=3):
    return (" " * padding) + str(string) + (" " * padding)


def __pad_all(iterable):
    return [__pad(i) for i in iterable]


def display_table(list_data, headers, title="Table"):
    # Calculate the maximum width for each column
    column_widths = {header: max(
        len(str(row[i])) for row in list_data) for i, header in enumerate(headers)}
    header_row = "|".join(
        f"{header.center(column_widths[header])}" for header in headers)

    # Display the title
    title_line = f"{title.center(len(header_row) + len(headers) - 1)}"
    print(title_line)
    print("-" * len(header_row))

    # Display the headers
    print(header_row)
    print("-" * len(header_row))

    # Display the data rows
    for row in list_data:
        row_str = "|".join(
            f"{str(row[i]).center(column_widths[header])}" for i, header in enumerate(headers))
        print(row_str)

    print()


def display_products(products: list[Product]):
    """
    Function for displaying the products passed.
    Parameter: products (list of Product objects)
    """
    print()
    headers = __pad_all(["Product ID", "Title", "Price"])
    data = [
        __pad_all([products.index(product) + 1,
                  product.title, f"Rs.{product.price}"])
        for product in products
    ]
    title = __pad("Products")
    display_table(data, headers, title)


def display_cart(cart: Cart):
    """
    Function for displaying the items inside the cart passed.
    Parameter: cart (Cart object)
    """
    print()
    title = __pad("Shopping Cart")
    headers = __pad_all([
        "Item ID", "Product Title", "Product Price", "Quantity", "Partial Bill"
    ])
    data = [
        __pad_all([cart.items.index(item) + 1, item.product.title,
                   f"Rs.{item.product.price}", item.quantity, f"Rs.{item.product.price * item.quantity}"])
        for item in cart.items
    ]
    display_table(data, headers, title)


def checkout_routine(cart: Cart, user: User):
    """
    Function for displaying the receipt of the items selected in the cart
    return True if successful else returns False
    """
    print()
    time.sleep(1)
    if cart.bill == 0:
        print("Add some products to cart first.")
    else:
        print("Proceeding to checkout...")
        print()
        print("###CART ITEMS###")
        print(f"Bill: Rs.{cart.bill}")
        time.sleep(1)

        display_cart(cart)
        print()
        print("Payment:")
        print(f"Account holder: {user.username}")
        bank_name = input("Enter the bank you want to pay with: ")
        print()
        password = input("Enter your account password: ")
        if password == user.password:
            print()
            print("Successfully authenticated.")
            print(f"Delivery address: {user.address}")
            confirmation = input("Press 'y' to confirm: ")
            if confirmation == "y":
                print()
                print("Success. Items will be delivered in 1 to 2 working days.")
                print("Thank you for shopping!")
                time.sleep(1)
                cart.bank_name = bank_name
                cart.timestamp = time.asctime()
                database.write_cart(user, cart)
                return True
            else:
                print()
                print("Checkout failed.")
    return False


def display_orders_summary(carts: list[Cart]):
    """
    Displays a summarized table of previous shopping histories.
    """
    print()
    title = __pad("History Summary")
    headers = __pad_all([
        "Order No.", "Bank Name", "Date/Time", "Item Count", "Bill"
    ])
    data = [
        __pad_all([carts.index(cart) + 1, cart.bank_name, cart.timestamp,
                   sum(item.quantity for item in cart.items), f"Rs.{cart.bill}"])
        for cart in carts
    ]
    display_table(data, headers, title)
