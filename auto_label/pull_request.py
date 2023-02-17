import re

from auto_label.base import BaseProcessor


class PullRequestProcessor(BaseProcessor):
    # https://docs.github.com/en/webhooks-and-events/events/github-event-types#pullrequestevent
    def __init__(self, client, event):
        super().__init__(client, event)
        self.action = self.event.get('action', None)
        self.pattern = re.compile(r"(- \[[x|X]\] (\w+)\r\n)")
        self.type_map = {
            "bug": "type/bug",
            "feature": "type/feature req",
            "enhancement": "type/enhancement",
        }
        if self.action is None:
            raise Exception("No action found")
        self.change_label = self.event.get('label', None)
        self.changes = self.event.get('changes', None)
        try:
            repo = self.event['repository']['full_name']
            self.repo = self.client.get_repo(repo)
            pr_num = self.event['pull_request']['number']
            self.pull_request = self.repo.get_pull(pr_num)
            labels = self.pull_request.get_labels()
            self.labels_name = [label.name for label in labels]
        except Exception as e:
            raise e
        print(">>> pr number: {}".format(self.pull_request.number))

    def run(self):
        if self.action == "opened":
            self.opened()
        elif self.action == "edited":
            self.edited()
        elif self.action == "labeled":
            self.labeled()
        elif self.action == "unlabeled":
            self.unlabeled()

    def remove_label(self, label):
        if label in self.labels_name:
            self.pull_request.remove_from_labels(label)

    def opened(self):
        b = self.pull_request.body
        m = self.pattern.findall(b)
        for i in m:
            t = i[1]
            if t not in self.type_map:
                continue

            print(">>> type: {}.\n".format(t))
            for original in self.type_map:
                self.remove_label(self.type_map[original])
            
            self.pull_request.add_to_labels(self.type_map[t])
            break

        self.verify_mandatory_labels()

    def edited(self):
        # simply check if body changed
        self.opened()

    def verify_mandatory_labels(self):
        mandatory_list = [
            "type",
        ]
        mandatory_check = [True for _ in range(len(mandatory_list))]
        labels = self.pull_request.get_labels()
        labels_name = [label.name for label in labels]
        for name in labels_name:
            for i in range(len(mandatory_list)):
                if name.startswith(mandatory_list[i] + "/"):
                    mandatory_check[i] = False

        for i in range(len(mandatory_check)):
            if mandatory_check[i]:
                self.pull_request.add_to_labels(mandatory_list[i] + "/none")
