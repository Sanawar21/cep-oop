"""
main.py file for minimum project requirements of CS-115 term project.
"""
from src import database
from models.product import Product
from models.cart import Cart
from src.routines import display_products, display_cart, checkout_routine, sign_up_routine, login_routine, admin_login_routine, display_orders_summary
import time


def main():
    print()
    print()
    print("================================")
    print("Welcome to Online Shopping Store!")
    print("================================")
    time.sleep(1)
    print("1. Login")
    print("2. Sign up")
    print("3. Quit")
    print("4. Admin Login")
    time.sleep(1)

    print()

    choice = int(input("Enter your choice: "))
    current_account = None  # initialize the current user handler.

    if choice == 1:
        print()
        current_account = login_routine()

        if current_account == None:  # check if user wants to quit.
            quit()
        else:
            print("Logged in successfully!")
        time.sleep(1)

    elif choice == 2:

        print()
        current_account = sign_up_routine()

        if current_account == None:  # check if user wants to quit.
            quit()
        else:
            print("Signed up successfully!")
        time.sleep(1)

    elif choice == 3:
        quit()
    elif choice == 4:
        while True:
            admin_return = admin_login_routine()
            if admin_return:
                products = database.get_products()

                print("Logged in Successfully")
                print()
                print("1.Add Product To The Inventory")
                print("2.Remove Product From The Inventory")
                print("3.Change Price of a Product")
                choice = int(input("Enter Command:"))

                if choice == 1:

                    title = input("Enter Product Title:")
                    price = int(input("Enter Price:"))
                    product = [Product(title, price)]
                    database.save_products(product)
                    print(f"{title} added successfully")

                elif choice == 2:
                    display_products(products)

                    product = input("Enter the Product Title:")
                    database.remove_product_inventory(product)
                    print(f"{product} removed successfully")

                elif choice == 3:
                    display_products(products)
                    product_title = input("Enter Product Title:")
                    new_price = int(input("Enter the new Price:"))
                    database.change_price(product_title, new_price)
                    print(f"{product_title} price changed successfully")

                else:
                    print("Enter a Valid Choice")

                __continue = input("To Start Again Press y").lower()
                if __continue == "y":
                    pass
                else:
                    quit()

            else:

                quit()

    else:
        print("Invalid choice. Please select a valid option to continue.")
        # Implementing recursive function in this case instead of while loop.
        main()

    # Below code only executes if there is a valid current_account.
    print()
    products = database.get_products()
    # this contains cart info for the current session
    cart = Cart(current_account.username)

    while True:
        time.sleep(1)
        print("1. View products list")
        print("2. Add products to cart")
        print("3. Remove products from cart")
        print("4. View cart")
        print("5. View shopping history")
        print("6. Checkout")
        print("7. Exit")
        print()
        time.sleep(0.5)

        choice = int(input("Enter your choice: "))

        if choice == 1:
            print()
            print("Displaying products...")
            time.sleep(0.5)
            display_products(products)
        elif choice == 2:
            print()
            print("Displaying products...")
            time.sleep(0.5)
            display_products(products)
            id = int(input("Enter product id to add: "))
            try:
                index = id - 1
                product = products[index]
                quantity = int(
                    input(f"Enter the quantity of '{product.title}': "))
                cart.add_product(product, quantity)
                print(f"{product.title} added to cart successfully.")

            except:
                print("Invalid product id.")
            print()
        elif choice == 3:
            if cart.bill == 0:
                print()
                print("You cart is empty. Nothing to remove from.")
            else:
                display_cart(cart)
                id = int(input("Enter item id to remove: "))
                try:
                    index = id - 1
                    product = cart.items[index].product
                    quantity = int(
                        input(f"Enter the quantity of '{product.title}' to remove: "))
                    cart.remove_product(product, quantity)
                    print(f"{product.title} removed from cart successfully.")

                except:
                    print("Invalid item id.")
                print()

        elif choice == 4:
            print()
            if cart.bill == 0:
                print("Cart is currently empty.")
            else:
                print("SHOPPING CART...")
                print(f"This is your total: RS.{cart.bill}")
                display_cart(cart)
        elif choice == 5:
            print()
            carts = database.read_carts(current_account)
            if carts != []:
                for i in range(len(carts)):
                    print(f"Order no. {i+1}")
                    print(f"Bank name: {carts[i].bank_name}")
                    print(f"Data and Time: {carts[i].timestamp}")
                    print(f"Address: {current_account.address}")
                    print(f"Bill: Rs.{carts[i].bill}")
                    display_cart(carts[i])
                    print()
                time.sleep(1)
                print()
                display_orders_summary(carts)
            else:
                print("No orders placed yet.")

        elif choice == 6:
            success = checkout_routine(cart, current_account)
            if success:
                cart = Cart(current_account.username)

        elif choice == 7:
            quit()
        else:
            print("Enter a valid choice.")


if __name__ == "__main__":
    main()
