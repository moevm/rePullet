from github import Github

from rePullet.logic.user import User


def getUserData(access_token):
    ghI = Github(login_or_token=access_token)
    user = ghI.get_user()
    userId = user.id
    name = user.login
    return User(userId, ghI, name)
