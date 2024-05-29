from abc import abstractmethod, ABC
from .cart import Cart
from .bank_details import BankDetails
from .product import Product
from .cart import Item
import time


class Order(ABC):
    def __init__(self, cart: Cart, full_name, address) -> None:
        self.owner = cart.owner
        self.full_name = full_name
        self.items = cart.items
        self.bill = cart.bill
        self.address = address
        self.timestamp = time.asctime()

    @classmethod
    @abstractmethod
    def null(cls):
        pass

    @abstractmethod
    def to_dict(self):
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls):
        pass


class BankOrder(Order):
    def __init__(self, cart: Cart, full_name, address, bank_details: BankDetails) -> None:
        super().__init__(cart, full_name, address)
        self.type = "Bank"
        self.bank_name = bank_details.bank_name
        self.card_number = bank_details.card_number

    @classmethod
    def null(cls):
        return cls(
            Cart.null(),
            None, None,
            BankDetails.null()
        )

    def to_dict(self):
        return {
            "owner": self.owner,
            "bill": self.bill,
            "timestamp": self.timestamp,
            "type": self.type,
            "full_name": self.full_name,
            "bank_name": self.bank_name,
            "card_number": self.card_number,
            "address": self.address,
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
    def from_dict(cls, data):
        obj = cls.null()
        obj.owner = data["owner"]
        obj.bill = data["bill"]
        obj.timestamp = data["timestamp"]
        obj.type = data["type"]
        obj.full_name = data["full_name"]
        obj.bank_name = data["bank_name"]
        obj.card_number = data["card_number"]
        obj.address = data["address"]
        obj.items = [Item(Product(attr["title"], attr["price"],
                          attr["uid"]), attr["quantity"]) for attr in data["items"]]
        return obj


class CodOrder(Order):
    def __init__(self, cart: Cart, full_name, address, email, phone) -> None:
        super().__init__(cart, full_name, address)
        self.type = "COD"
        self.email = email
        self.phone = phone
        self.address = address

    @classmethod
    def null(cls):
        return cls(
            Cart.null(), None, None, None, None
        )

    def to_dict(self):
        return {
            "owner": self.owner,
            "bill": self.bill,
            "timestamp": self.timestamp,
            "type": self.type,
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
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
    def from_dict(cls, data):
        obj = cls.null()
        obj.owner = data["owner"]
        obj.bill = data["bill"]
        obj.timestamp = data["timestamp"]
        obj.type = data["type"]
        obj.full_name = data["full_name"]
        obj.email = data["email"]
        obj.phone = data["phone"]
        obj.address = data["address"]
        obj.items = [Item(Product(attr["title"], attr["price"],
                          attr["uid"]), attr["quantity"]) for attr in data["items"]]
        return obj
