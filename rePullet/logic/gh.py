from github import Github

from rePullet.logic.user import User


def getUserData(access_token):
    ghI = Github(login_or_token=access_token)
    userId = ghI.get_user().id
    return User(userId, ghI)
