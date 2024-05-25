class Product:
    """
    Product object for handling products in the store.    
    """

    def __init__(self, title, price) -> None:
        self.title = title
        self.price = price

    def __str__(self) -> str:
        as_string = f"Title: {self.title}\nPrice: Rs.{self.price}"

        return as_string
