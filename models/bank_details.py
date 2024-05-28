class BankDetails:

    def __init__(self, owner, bank_name, card_number, pin) -> None:
        self.owner = owner
        self.bank_name = bank_name
        self.card_number = card_number
        self.pin = pin

    def to_dict(self):
        return {
            "owner": self.owner,
            "bank_name": self.bank_name,
            "card_number": self.card_number,
            "pin": self.pin,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["owner"],
            data["bank_name"],
            data["card_number"],
            data["pin"],
        )
