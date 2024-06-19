from .base_app import BaseApp
from ..utils import only_allow, completion, failure, Paths as paths

from ..models.authenticate import Authenticator
from ..models.database import Database
from ..models.cart import Cart
from ..models.product import Product
from ..models.product import Product
from ..models.account import User, Admin, Privilege
from ..models.bank_details import BankDetails
from ..models.order import BankOrder, CodOrder


class UserApp(BaseApp):
    def __init__(self, user: User):
        super().__init__(
            user,
            "user",
            __name__,
            paths.templates,
            [User]
        )
