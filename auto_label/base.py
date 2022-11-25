from github import Github


class BaseProcessor(object):
    def __init__(self, client: Github, event: dict):
        self.client = client
        self.event = event
