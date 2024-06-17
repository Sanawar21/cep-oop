from .product import Product


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
        as_string = f"Title: {self.product.title}\nPrice: Rs.{
            self.product.price}\nQuantity: {self.quantity}"

        return as_string


class Cart:
    """
    Cart object for handling the shopping current within the application.
    This will only be a part of the main memory.    
    """

    def __init__(self, uid) -> None:
        self.uid = uid
        # will save items as Item objects
        self.items: list[Item] = []
        self.get_bill()

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
        obj.bill = data["bill"]
        obj.items = [
            Item(Product(attr["title"], attr["price"], attr["uid"]), attr["quantity"]) for attr in data["items"]
        ]
        return obj

    def get_bill(self):
        bill = 0
        for item in self.items:
            bill += item.product.price * item.quantity
        self.bill = bill
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
        self.get_bill()

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
        self.get_bill()
