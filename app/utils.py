import os
from .models.cart import Cart
from .models.account import Privilege, Admin, User, Account

from flask import redirect, url_for, render_template, session
from collections.abc import Callable


def failure(action_detail, back_link):
    template = "./admin/failure.html"
    return render_template(template, action_detail=action_detail, back_link=back_link)


def completion(action_detail, back_link):
    template = "./admin/completion.html"
    return render_template(template, action_detail=action_detail, back_link=back_link)


def only_allow(account: Admin | User, types_: list[type] | type):
    """
    Some routes are only accessible to specific account types.
    For example, only a User account can checkout, Only a privileged Admin can
    edit products list.

    This wrapper forces this functionality. It reroutes the app to the login page
    if the current account type is not the allowed account type passed in the `types_` argument.

    The programmer can also add a list of allowed types.
    """
    if type(types_) != list:
        types_ = [types_]  # Convert the types_ argument into a list

    def decorator(func):
        def wrapper(*args, **kwargs):
            if type(account) not in types_:
                return redirect(url_for('logout'))
            else:
                return func(*args, **kwargs)

        # This is important because flask searches endpoints with the function names.
        # So if all functions are named `wrapper`, flask cannot differentiate between routes.
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper.__module__ = func.__module__

        return wrapper
    return decorator


def check_privilege(account: Admin | User, privilege: str = None):
    """
    THIS DECORATOR IS OVERLOADED
    if arg is passed, then the route for which the privilege will be checked will be the
    arg.
    else the function name will be checked
    """

    def decorator(func: Callable):

        route_name = func.__name__ if not privilege else privilege

        def wrapper(*args, **kwargs):
            if route_name not in Privilege.ALL or account.has_privilege(route_name.upper()):
                return func(*args, **kwargs)
            else:
                return failure("You do not have the privilege to perform this action.", url_for("admin"))

        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper.__module__ = func.__module__

        return wrapper

    return decorator


class Path(str):
    # weak class, not robust but works for our case.
    # removes the need to import addtional package (pathlib).

    @property
    def name(self):
        return os.path.basename(self)

    def __truediv__(self, other):
        return Path(os.path.join(self, other))


class Paths:
    # base paths
    base = Path(os.getcwd())
    templates = base / "templates"
    database = base / "database"
    static = base / "static"

    images = static / "images"

    # templates paths

    # admin
    admin_templates_base = templates / "admin"
    admin_template = admin_templates_base / "admin.html"
    completion_template = admin_templates_base / "completion.html"
    failure_template = admin_templates_base / "failure.html"

    # admin changes
    admin_changes_templates_base = admin_templates_base / "changes"
    changes_admin_template = admin_changes_templates_base / "admin.html"
    changes_user_template = admin_changes_templates_base / "user.html"
    changes_product_template = admin_changes_templates_base / "product.html"

    # admin adds
    admin_add_templates_base = admin_templates_base / "add"
    add_admin_template = admin_add_templates_base / "admin.html"
    add_user_template = admin_add_templates_base / "user.html"
    add_product_template = admin_add_templates_base / "product.html"

    # admin edits
    admin_edit_templates_base = admin_templates_base / "edit"
    edit_admin_template = admin_edit_templates_base / "admin.html"
    edit_user_template = admin_edit_templates_base / "user.html"
    edit_product_template = admin_edit_templates_base / "product.html"

    # checkout paths
    checkout_templates_base = templates / "checkout"
    checkout_bank_template = checkout_templates_base / "checkout_bank.html"
    checkout_cod_template = checkout_templates_base / "checkout_cod.html"

    # store paths
    store_templates_base = templates / "store"
    cart_template = store_templates_base / "cart.html"
    history_template = store_templates_base / "history.html"
    products_template = store_templates_base / "products.html"
    product_detail_template = store_templates_base / "product_detail.html"

    # auth paths
    authentication_templates_base = templates / "user_authentication"
    bank_details_template = authentication_templates_base / "bank_detail.html"
    index_template = authentication_templates_base / "index.html"
    login_template = authentication_templates_base / "login.html"
    sign_up_template = authentication_templates_base / "signup.html"
