import os
import json
from github import Github
from auto_label.issue import IssueProcessor


def test_open_issue():
    token = 'ghp_xxx'
    with open("tests/issue_event.json", "r") as fl:
        event = json.load(fl)

    gh = Github(token)
    i = IssueProcessor(gh, event)
    i.run()
