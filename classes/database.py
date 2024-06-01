"""
Database handler for this project.
"""

from .cart import Cart
from .product import Product
from .account import User, Admin, Account
from .order import CodOrder, BankOrder

import random


class Database:

    SEP = "@#$%"

    def get_products(self) -> "list[Product]":
        """
        Returns a list of products stored in the database as Product objects.
        """

        products = []

        with open("database/products.txt") as file:
            lines = file.readlines()
            for line in lines:
                attrs = line.strip().split(self.SEP)
                products.append(
                    Product(attrs[0], int(float(attrs[1])), uid=attrs[2]))

        return products

    def save_products(self, products: "list[Product]"):
        """
        Writes the products list provided to the database.
        """

        with open("database/products.txt", "a") as file:
            file.writelines([
                f"{product.title}{self.SEP}{product.price}{
                    self.SEP}{product.uid}\n"
                for product in products
            ])

    def get_accounts(self) -> list[Admin | User]:
        accounts = []
        with open("database/accounts.txt") as file:
            lines = file.readlines()
            for line in lines:
                data = eval(line.strip())
                if data["type"] == User.type:
                    account = User.from_dict(data)
                elif data["type"] == Admin.type:
                    account = Admin.from_dict(data)
                accounts.append(account)
        return account

    def save_accounts(self, accounts: list[User | Admin]):
        # remove all file contents
        with open("database/accounts.txt", "w") as file:
            pass
        # rewrite the users
        for account in accounts:
            self.save_account(account)

    def overwrite_account(self, new_account: User | Admin):
        accounts = self.get_accounts()
        index = None
        for i, account in enumerate(accounts):
            if account.username == new_account.username:
                index = i
                break
        else:
            return

        accounts[index] = new_account
        self.save_accountsc(accounts)
        return new_account

    def save_account(self, account: User | Admin):
        """
        Saves a (new) User or Admin object to database. 
        """
        with open("database/accounts.txt", "a") as file:
            file.write(str(account.to_dict()) + "\n")

    def remove_product_inventory(self, product_title: str):
        """this function reads the old file remove the product and writes the new file,
        it takes Product.title as a parameter"""

        with open("database/products.txt") as file:
            lines = file.readlines()
            new_lines = []
            for line in lines:
                if line in lines:
                    if not line.startswith(f"{product_title}{self.SEP}"):
                        new_lines.append(line)
            with open("database/products.txt", "w") as file_:
                file_.writelines(new_lines)

    def change_price(self, product_title: str, new_price: int):
        """this functions reads the old file access the product and change its price and writes new file and it takes """

        with open("database/products.txt") as file:
            lines = file.readlines()
            new_lines = []
            for line in lines:
                if line.startswith(f"{product_title}{self.SEP}"):
                    new_line = f"{product_title}{self.SEP}{new_price}\n"
                    new_lines.append(new_line)
                else:
                    new_lines.append(line)
            with open("database/products.txt", "w") as file_:
                file_.writelines(new_lines)

    @staticmethod
    def write_order(order: BankOrder | CodOrder):
        with open(f"database/order_histories/{order.owner}", "a") as file:
            file.write(str(order.to_dict())+"\n")

    @staticmethod
    def read_orders(owner: str) -> list[BankOrder | CodOrder]:
        orders = []
        try:
            with open(f"database/order_histories/{owner}") as file:
                lines = file.readlines()
                for line in lines:
                    if line != "" or line != "\n":
                        order_data = eval(line.strip())
                        if order_data["type"] == CodOrder.type:
                            orders.append(CodOrder.from_dict(order_data))
                        else:
                            orders.append(BankOrder.from_dict(order_data))
        except FileNotFoundError:
            pass
        return orders

    def get_product(self, uid):
        return [product for product in self.get_products() if product.uid == uid][0]

    @staticmethod
    def generate_uid():
        alphabets = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        characters = alphabets + alphabets.lower() + "".join(str(i)
                                                             for i in range(10))
        uid = ''.join(random.choices(characters, k=12))
        return uid
