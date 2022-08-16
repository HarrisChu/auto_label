import os
from datetime import datetime, timedelta
from github import Github

gh_url = "https://github.com"
token = os.environ["GH_PAT"]
gh = Github(token)
issue_labels = os.environ["ISSUE_LABEL"]
pr_labels = os.environ["PR_LABEL"]


def get_yesterday_time():
    today = datetime.today()
    yesterday = today - timedelta(days=1)
    return yesterday


def check_element_label(element, label):
    for i in element.labels:
        li = i.name.split("/")
        if label in li:
            return True
    return False


def get_issues(repo):
    list_issue = []
    for type_state in ["open", "closed"]:
        for issue in repo.get_issues(state=type_state):
            if not issue.pull_request:
                list_issue.append(issue)
            if issue.created_at < get_yesterday_time():
                break
    return list_issue


def get_prs(repo):
    list_pr = []
    for pr in repo.get_pulls("all"):
        list_pr.append(pr)
        if pr.created_at < get_yesterday_time():
            break
    return list_pr

def auto_delete_default(element):
    li_none=[]
    for each in element.labels:
        li = each.name.split("/")
        if li[1] == 'none':
            li_none.append(li[0])
    for each in element.labels:
        li = each.name.split("/")
        if li[0] in li_none and li[1] != 'none':
            element.remove_from_labels('{}/none'.format(li[0]))

def mod_pr_issue_label(list_element, label):
    for element in list_element:
        if check_element_label(element, label) == False:
            # element.set_labels(*element.labels, "{}/none".format(label))
            element.add_to_labels("{}/none".format(label))
        else:
            auto_delete_default(element)


def main(repo_name, issue_num, pr_num):
    list_issue_label = issue_labels.split(";")
    list_pr_label = pr_labels.split(";")
    repo = gh.get_repo(repo_name)
    list_issues = []
    list_prs = []
    if issue_num:
        git_issue = repo.get_issue(issue_num)
        list_issues.append(git_issue)
    else:
        list_issues = get_issues(repo)
    for each in list_issue_label:
        mod_pr_issue_label(list_issues, each)

    if pr_num:
        git_pr = repo.get_pull(pr_num)
        list_prs.append(git_pr)
    else:
        list_prs = get_prs(repo)

    for each in list_pr_label:
        mod_pr_issue_label(list_prs, each)


if __name__ == "__main__":
    repo_name = os.environ["GITHUB_REPOSITORY"]
    issue_num = os.environ["IU_NUM"]
    pr_num = os.environ["PR_NUM"]
    # issue_num="31"
    # pr_num=""
    if issue_num != "":
        issue_num = int(issue_num)
    if pr_num != "":
        pr_num = int(pr_num)

    print(">>> issue number: {}, pr number: {}".format(issue_num, pr_num))
    main(repo_name, issue_num, pr_num)
