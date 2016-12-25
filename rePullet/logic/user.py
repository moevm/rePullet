from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, id, ghI, name):
        self.id = id
        self.ghI = ghI
        self.name = name

    @property
    def is_authenticated(self):
        if self.ghI is not None:
            return True

    def __repr__(self):
        return "%s" % self.id
