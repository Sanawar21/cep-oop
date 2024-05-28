class User:
    """
    User object for handling users in the store. 
    Every User has a unique username.
    """

    def __init__(self, username, password, full_name, address) -> None:
        self.username = username
        self.password = password
        self.full_name = full_name
        self.address = address


class Admin(User):

    def __init__(self) -> None:
        super().__init__("admin", "shopping123", "Admin",
                         "CIS Department, NED University, Karachi.")
