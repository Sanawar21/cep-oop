"""
Database handler for this project.
"""

from .product import Product
from .account import User, Admin
from .order import CodOrder, BankOrder
from .cart import Cart

from ..utils import Paths as paths

import random


class Database:

    # product methods

    def get_products_paginated(self, page, per_page):
        products = self.get_products()
        start = (page - 1) * per_page
        end = start + per_page
        paginated_products = products[start:end]
        total_products = len(products)
        return paginated_products, total_products

    @staticmethod
    def get_products() -> "list[Product]":
        """
        Returns a list of products stored in the database as Product objects.
        """

        products = []

        with open("database/products.txt") as file:
            lines = file.readlines()
            for line in lines:
                data = eval(line.strip())
                products.append(Product.from_dict(data))

        return products

    def get_product(self, uid):
        for product in self.get_products():
            if product.uid == uid:
                return product

    @staticmethod
    def save_product(product: Product):
        with open("database/products.txt", "a") as file:
            file.write(f"{product.to_dict()}\n")

    def save_products(self, products: "list[Product]"):
        """
        Writes the products list provided to the database.
        """
        # remove all file contents
        with open("database/products.txt", "w"):
            pass
        # rewrite the products
        for product in products:
            self.save_product(product)

    def overwrite_product(self, new_product):
        products = self.get_products()
        index = None
        for i, product in enumerate(products):
            if product.uid == new_product.uid:
                index = i
                break
        else:
            return

        products[index] = new_product
        self.save_products(products)
        return new_product

    def delete_product(self, uid):
        products = self.get_products()
        products.remove(self.get_product(uid))
        self.save_products(products)

    # account methods

    def get_account(self, uid) -> Admin | User | None:
        for account in self.get_accounts():
            if account.uid == uid:
                return account

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
        return accounts

    def save_accounts(self, accounts: list[User | Admin]):
        # remove all file contents
        with open("database/accounts.txt", "w"):
            pass
        # rewrite the users
        for account in accounts:
            self.save_account(account)

    def overwrite_account(self, new_account: User | Admin):
        accounts = self.get_accounts()
        index = None
        for i, account in enumerate(accounts):
            if account.uid == new_account.uid:
                index = i
                break
        else:
            return

        accounts[index] = new_account
        self.save_accounts(accounts)
        return new_account

    def save_account(self, account: User | Admin):
        """
        Saves a (new) User or Admin object to database. 
        """
        with open("database/accounts.txt", "a") as file:
            file.write(str(account.to_dict()) + "\n")

    def delete_account(self, uid):
        accounts = self.get_accounts()
        for account in accounts:
            if account.uid == uid:
                accounts.remove(account)
                break
        self.save_accounts(accounts)

    # order methods

    @staticmethod
    def write_order(order: BankOrder | CodOrder, owner_uid):
        with open(f"database/order_histories/{owner_uid}", "a") as file:
            file.write(str(order.to_dict())+"\n")

    @staticmethod
    def read_orders(owner_uid: str) -> list[BankOrder | CodOrder]:
        orders = []
        try:
            with open(f"database/order_histories/{owner_uid}") as file:
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

    # miscellaneous

    @staticmethod
    def generate_uid():
        alphabets = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        characters = alphabets + alphabets.lower() + "".join(str(i)
                                                             for i in range(10))
        uid = ''.join(random.choices(characters, k=12))
        return uid
