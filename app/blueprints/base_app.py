from ..utils import only_allow, check_privilege, Paths as paths
from ..models.database import Database
from ..models.authenticate import Authenticator
from ..models.account import Admin, User

from flask import Blueprint
from abc import ABC, abstractmethod


class BaseApp(Blueprint, ABC):
    def __init__(self, account: User | Admin, name, import_name, templates):
        super().__init__(
            name,
            import_name,
            static_folder=paths.static,
            template_folder=templates,
        )

        self.account = account
        self.database = Database()
        self.authenticator = Authenticator()
        self.add_routes()

    def register_route(self, route, types_: list[type]):
        self.add_url_rule(f"/{route.__name__}", view_func=only_allow(
            self.account, types_)(check_privilege(self.account)(route)))

    @abstractmethod
    def add_routes():
        pass
