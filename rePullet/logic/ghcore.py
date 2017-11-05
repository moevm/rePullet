import os.path
from urllib.parse import urlparse

import github
from github import Github
from github.Issue import Issue
from github.PullRequest import PullRequest
from github.Repository import Repository

from rePullet.logic.user import User


#github.enable_console_debug_logging()

def count_rebuild(issue, pull):
    """
    @type issue: Issue
    @type pull: PullRequest
    """
    rebuild = 0
    if pull.comments != 0:
        issuecomments = issue.get_comments()
        pullcommits = pull.get_commits()
        startcomment = issuecomments[0]
        for comment in issuecomments:
            for commit in pullcommits:
                if startcomment.created_at < commit.commit.committer.date < comment.created_at:
                    rebuild += 1  # защитывается только одна доделка
                    break
            startcomment = comment
        for commit in pullcommits:
            if commit.commit.committer.date > startcomment.created_at:
                rebuild += 1
                break
    return rebuild


def countReport(pull):
    """
    :param pull: PullRequest
    :type pull: PullRequest
    :return: bool
    """
    count = 0
    for fl in pull.get_files():
        if (fl.filename.endswith(".pdf")
            or fl.filename.endswith(".doc")
            or fl.filename.endswith(".docx")):
            count += 1
    return count

def getUserData(access_token):
    try:
        ghI = Github(login_or_token=access_token, timeout=25)
        user = ghI.get_user()
        #print(user)
        name = ghI.get_user().login
        avatar = ghI.get_user().avatar_url
        userid = ghI.get_user().id
        html_url = ghI.get_user().html_url
        #print(ghI.rate_limiting)
        return User(userid, ghI, name, avatar, html_url)
    except:
        print('lol')


def getrepoid(user, url):
    # TODO: проверка url на валидность
    path = urlparse(url).path
    prev = ''
    while os.path.dirname(path) != '/':
        prev = path
        path = os.path.dirname(path)
    path = prev[1:]
    repo = user.ghI.get_repo(path)
    if repo:
        return repo.id
    return None


def getRepoNameById(user, id):
    try:
        return user.ghI.get_repo(id).full_name
    except github.GithubException:
        return None

def getRepoIdByName(user, reponame):
    try:
        return user.ghI.get_repo(reponame).id
    except github.GithubException:
        return None

def is_colown(user, id):
    try:
        if user.ghI.get_repo(id).owner.login == user.name:
            return True
        return user.ghI.get_repo(id).has_in_collaborators(user.name)
    except github.GithubException:
        return False

def getUserName(user, login):
    try:
        a = user.ghI.get_user(login)
        if a and a.name:
            return a.name
        return login
    except github.GithubException:
        return None

def downloadMaster(user, id):
    try:
        a = user.ghI.get_repo(id).get_archive_link('tarball')
        print ("Url = " + str(a))
        return a
    except github.GithubException:
        return None