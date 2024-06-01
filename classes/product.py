class Product:
    """
    Product object for handling products in the store.    
    """

    def __init__(self, title, price, uid=None) -> None:
        self.title = title
        self.price = price
        self.uid = uid
        if uid:
            self.image_path = f"static/images/{self.uid}.jpg"
        else:
            self.image_path = "static/images/placeholder_image.jpg"

    def __eq__(self, value: object) -> bool:
        if isinstance(value, Product):
            return self.uid == value.uid
        return False

    def __str__(self) -> str:
        as_string = f"Title: {self.title}\nPrice: Rs.{self.price}"

        return as_string
