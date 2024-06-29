from .product import Product
from flask import session


class Item:
    """
    For managing Product objects and their quantities.
    """

    def __init__(self, product: Product, quantity: int) -> None:
        self.product = product
        self.quantity = quantity

    def __eq__(self, __value: object) -> bool:
        # return True if the objects are identical or the other object is the same Product object as in the Item
        if isinstance(__value, Item):
            return self.product.uid == __value.product.uid
        elif isinstance(__value, Product):
            return self.product.uid == __value.uid
        # for other cases return False
        else:
            return False

    def __str__(self) -> str:
        as_string = f"Title: {self.product.title}\nPrice: Rs.{self.product.price}\nQuantity: {self.quantity}"

        return as_string


class Cart:
    """
    Cart object for handling the shopping current within the application.
    This will only be a part of the main memory.    
    """

    def __init__(self, uid) -> None:
        # will save items as Item objects
        self.items: list[Item] = []
        self.uid = uid

    def to_dict(self):
        return {
            "uid": self.uid,
            "bill": self.bill,
            "items": [
                {
                    "uid": item.product.uid,
                    "title": item.product.title,
                    "price": item.product.price,
                    "quantity": item.quantity,
                } for item in self.items
            ]
        }

    @classmethod
    def null(cls):
        return cls(None)

    @classmethod
    def from_dict(cls, data: dict):
        """
        Changes currect cart to the data provided in the dictionary
        """
        obj = cls.null()
        obj.uid = data["uid"]
        obj.items = [
            Item(Product(attr["title"], attr["price"], attr["uid"]), attr["quantity"]) for attr in data["items"]
        ]
        return obj

    @property
    def bill(self):
        """Total bill of the current cart."""
        bill = 0
        for item in self.items:
            bill += item.product.price * item.quantity
        return bill

    def add_product(self, product: Product, quantity: int):
        """
        Adds a product to the cart.
        """
        if product not in self.items:
            self.items.append(Item(product, quantity))
        else:
            index = self.items.index(product)
            self.items[index].quantity += quantity

    def remove_product(self, product: Product, quantity: int):
        """
        Removes the Product object from the cart by quantity.
        If quantity >= quantity in the cart, then the product gets 
        removed from the cart. Else its quantity gets decreased by the amount
        specified.
        """
        in_items = self.items[self.items.index(product)]

        if in_items.quantity <= quantity:
            self.items.remove(in_items)
        else:
            in_items.quantity -= quantity


class SessionCart(Cart):
    """
    For keeping track of the cart with respect to the current session.
    """

    def __init__(self) -> None:
        data = session.get("cart")
        if data:
            self.items = [
                Item(Product(attr["title"], attr["price"], attr["uid"]), attr["quantity"]) for attr in data["items"]
            ]
            self.uid = data["uid"]
        else:
            self.items = []
            self.uid = None
        self.update()

    @property
    def uid(self):
        return self.__uid

    @uid.setter
    def uid(self, value):
        self.__uid = value
        self.update()

    def update(self):
        session["cart"] = self.to_dict()

    @classmethod
    def null(cls):
        session["cart"] = None
        return cls()

    def add_product(self, product: Product, quantity: int):
        super().add_product(product, quantity)
        self.update()

    def remove_product(self, product: Product, quantity: int):
        super().remove_product(product, quantity)
        self.update()
