from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, id, ghI, name, avatar, html_url):
        self.id = id
        self.ghI = ghI
        self.name = name
        self.avatar = avatar
        self.html_url = html_url

    @property
    def is_authenticated(self):
        if self.ghI is not None:
            return True

    def __repr__(self):
        return "%s" % self.id
