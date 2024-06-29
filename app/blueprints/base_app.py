from ..utils import Paths as paths
from ..models.database import Database
from ..models.authenticate import Authenticator
from ..models.account import Admin, User

from flask import Blueprint, session
from abc import ABC, abstractmethod
from collections.abc import Callable


class BaseApp(Blueprint, ABC):
    def __init__(self, name, import_name, templates, allowed_types: list[type], statics=paths.static, allowed_methods=["GET", "POST"]):
        super().__init__(
            name,
            import_name,
            static_folder=statics,
            template_folder=templates,
        )

        self.allowed_types = allowed_types
        self.allowed_methods = allowed_methods
        self.database = Database()
        self.authenticator = Authenticator()
        self.add_routes()

    @property
    def account(self):
        """Handler for the account in the current session."""
        try:
            uid = session.get("account_uid")
        except RuntimeError:
            return None
        if uid:
            return self.database.get_account(uid)
        else:
            return None

    @account.setter
    def account(self, obj: User | Admin | None):
        if obj:
            session["account_uid"] = obj.uid
        else:
            session["account_uid"] = None

    def register_route(self, route_handler: Callable):
        """
        Applies decorators to the routes and adds them to the blueprint
        """
        route_code = route_handler.__code__
        route_name = f"/{route_handler.__name__}/" + "/".join(
            [f"<{route_code.co_varnames[i]}>" for i in range(route_code.co_argcount) if i])

        # if Admin in self.allowed_types:
        #     view_func = only_allow(
        #         self.account,
        #         self.allowed_types,
        #     )(check_privilege(self.account)(route_handler))
        # else:
        #     view_func = only_allow(
        #         self.account, self.allowed_types)(route_handler)

        self.add_url_rule(
            route_name,
            view_func=route_handler,
            methods=self.allowed_methods
        )

    @abstractmethod
    def add_routes(self):
        """
        format:
        all_routes = [
            self.route1,
            self.route2,
            self.route3,
        ]

        for route in all_routes:
            self.register_route(route)

        """
        pass
