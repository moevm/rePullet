from github.PullRequest import PullRequest
from github.Issue import Issue

def count_rebuild(issue, pull):
    """
    @type issue: Issue
    @type pull: PullRequest
    """
    rebuild = 0
    issuecomments = issue.get_comments()
    pullcommits = pull.get_commits()
    startcomment = issuecomments[0]
    for comment in issuecomments:
        for commit in pullcommits:
            if startcomment.created_at < commit.commit.committer.date < comment.created_at:
                rebuild += 1 #защитывается только одна доделка
                break
        startcomment = comment
    for commit in pullcommits:
        if commit.commit.committer.date > startcomment.created_at:
            rebuild+=1
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
            count+=1
    return count