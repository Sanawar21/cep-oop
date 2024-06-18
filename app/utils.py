import os


class Path(str):
    # weak function, not robust but works for our case.
    # removes the need to import addtional package (pathlib).
    def __truediv__(self, other):
        if isinstance(other, (Path, str)):
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
