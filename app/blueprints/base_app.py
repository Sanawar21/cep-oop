from ..utils import only_allow, check_privilege, Paths as paths
from ..models.database import Database
from ..models.authenticate import Authenticator
from ..models.account import Admin, User

from flask import Blueprint
from abc import ABC, abstractmethod
from collections.abc import Callable


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

    def register_route(self, route: Callable, types_: list[type], methods: list[str]):
        route_name = f"/{route.__name__}/" + \
            "/".join([f"<{route.__code__.co_varnames[i]
                          }>" for i in range(route.__code__.co_argcount) if i])

        self.add_url_rule(
            route_name,
            view_func=only_allow(
                self.account,
                types_
            )(check_privilege(self.account)(route)),
            methods=methods
        )

    @abstractmethod
    def add_routes():
        pass
