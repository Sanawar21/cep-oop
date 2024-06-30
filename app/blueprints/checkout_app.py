from .base_app import BaseApp
from ..utils import Paths as paths

from ..models.cart import SessionCart
from ..models.account import User
from ..models.order import CodOrder, BankOrder, BankDetails

from flask import request, render_template


class CheckoutApp(BaseApp):
    def __init__(self):
        super().__init__(
            "checkout",
            __name__,
            paths.templates,
            [User],
            # not working; changes made in html template paths instead
            statics=paths.static + "/.."
        )

    def add_routes(self):
        # self.index = only_allow(self.account, [User])(self.index)
        self.add_url_rule("/", view_func=self.index)

        all_routes = [
            self.cod,
            self.bank,
        ]

        for route in all_routes:
            self.register_route(route)

    def index(self):
        self.cart = SessionCart()
        if self.account.bank_details:
            return render_template("./checkout/checkout_bank.html", user=self.account)
        else:
            return render_template("./checkout/checkout_cod.html", user=self.account)

    def cod(self):
        if request.method == 'POST':
            address = request.form['address']
            full_name = request.form['full_name']
            password = request.form['password']
            email = request.form['email']
            phone = request.form['phone']

            dummy_user = User(
                None,
                self.account.username,
                self.account.password,
                full_name,
                address,
                self.account.bank_details,
            )

            if not address or not full_name or not password or not email or not phone:
                return render_template('./checkout/checkout_cod.html',
                                       # implemented dummy account here
                                       user=dummy_user,
                                       email=email,
                                       phone=phone,
                                       password=password,
                                       error="All fields are required.")

            if password == self.account.password:
                order = CodOrder(self.database.generate_uid(), self.cart,
                                 full_name, address, email, phone)
                self.database.write_order(order, self.account.uid)
                self.cart = SessionCart.null()
                return render_template('./user_authentication/thankyou.html')

            else:
                return render_template('./checkout/checkout_cod.html',
                                       user=dummy_user,
                                       email=email,
                                       phone=phone,
                                       password=password,
                                       error="Incorrect account password.")

        return render_template('./checkout/checkout_cod.html', user=self.account)

    def bank(self):
        if request.method == "POST":

            # get details

            address = request.form["address"]
            full_name = request.form["full_name"]
            if self.account.bank_details:
                pin = request.form["pin"]
            else:  # bank details were passed right now
                bank_name = request.form["bank_name"]
                card_number = request.form["card_number"]
                pin = request.form["pin"]

            # for state management
            dummy_user = User(
                None,
                self.account.username,
                self.account.password,
                full_name,
                address,
                self.account.bank_details if self.account.bank_details else BankDetails(
                    bank_name, card_number, pin,
                )
            )

            # check validity

            if self.account.bank_details:
                if not pin or not address or not full_name:
                    return render_template(
                        './checkout/checkout_bank.html',
                        error="All fields are required.",
                        user=dummy_user,
                        first_bank_checkout=self.account.bank_details == None,
                    )

                if not self.account.check_pin(pin):
                    return render_template(
                        './checkout/checkout_bank.html',
                        error="Incorrect pin.",
                        user=dummy_user,
                        first_bank_checkout=self.account.bank_details == None,
                    )
            else:
                if not bank_name or not card_number or not pin or not address or not full_name:
                    return render_template(
                        "./checkout/checkout_bank.html",
                        error="All fields are required.",
                        user=dummy_user,
                        first_bank_checkout=self.account.bank_details == None,
                    )
                if not BankDetails.validate_card_number(card_number):
                    return render_template(
                        "./checkout/checkout_bank.html",
                        error="Card number must be 10 digits.",
                        user=dummy_user,
                        first_bank_checkout=self.account.bank_details == None,
                    )

                if not BankDetails.validate_pin(pin):
                    return render_template(
                        "./checkout/checkout_bank.html",
                        error="Pin must be 4 digit long.",
                        user=dummy_user,
                        first_bank_checkout=self.account.bank_details == None,
                    )

            if not self.account.bank_details:
                with_bank_details = self.account
                with_bank_details.add_bank_details(bank_name, card_number, pin)
                self.database.overwrite_account(
                    with_bank_details)
                self.account = with_bank_details

            # details are valid and usable
            order = BankOrder(self.database.generate_uid(), self.cart, self.account.full_name,
                              address, self.account.bank_details)

            self.database.write_order(order, self.account.uid)
            self.cart = SessionCart.null()
            return render_template('./user_authentication/thankyou.html')

        return render_template('./checkout/checkout_bank.html', user=self.account, first_bank_checkout=self.account.bank_details == None)
