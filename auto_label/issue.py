from auto_label.base import BaseProcessor


class IssueProcessor(BaseProcessor):
    # https://docs.github.com/en/developers/webhooks-and-events/events/github-event-types#issuesevent
    def __init__(self, client, event):
        super().__init__(client, event)
        self.action = self.event.get('action', None)
        self.change_label = self.event.get('label', None)
        try:
            repo = self.event['repository']['full_name']
            self.repo = self.client.get_repo(repo)
            issue_num = self.event['issue']['number']
            self.issue = self.repo.get_issue(issue_num)
        except Exception as e:
            raise e
        print(">>> issue number: {}".format(self.issue.number))

    def run(self):
        if self.action is None:
            raise Exception("No action found")

        if self.action == "opened" or self.action == "reopened":
            self.opened()
        elif self.action == "closed":
            self.closed()
        elif self.action == "labeled":
            self.labeled()
        elif self.action == "unlabeled":
            self.unlabeled()

    def opened(self):
        # if open or reopen, then delete "process/fixed", "process/done"
        # verify the mandatory labels, "affects/xxx", "severity/xxx"
        try:
            self.issue.remove_from_labels("process/fixed")
            self.issue.remove_from_labels("process/done")
        except:
            # ignore if not exist
            pass
        self.verify_mandatory_labels()

    def closed(self):
        # add "process/fixed"
        self.issue.add_to_labels("process/fixed")

    def labeled(self):
        # when add severity, should delete other severity labels.
        modify_list = ["severity"]
        if self.change_label is None:
            return
        labels = self.issue.get_labels()
        labels_name = [label.name for label in labels]

        for each in modify_list:
            if not self.change_label['name'].startswith(each + "/"):
                continue

            for name in labels_name:
                if name.startswith(each + "/") and name != self.change_label['name']:
                    self.issue.remove_from_labels(name)

    def unlabeled(self):
        # unable "type/bug", then delete "process/fixed", "process/done"
        if self.change_label is None:
            return
        if self.change_label['name'] == "type/bug":
            try:
                self.issue.remove_from_labels("process/fixed")
                self.issue.remove_from_labels("process/done")
            except:
                # ignore if not exist
                pass

    def verify_mandatory_labels(self):
        mandatory_list = ["affects", "type", "severity"]
        mandatory_check = [True for _ in range(len(mandatory_list))]
        labels = self.issue.get_labels()
        labels_name = [label.name for label in labels]
        for name in labels_name:
            for i in range(len(mandatory_list)):
                if name.startswith(mandatory_list[i] + "/"):
                    mandatory_check[i] = False

        for i in range(len(mandatory_check)):
            if mandatory_check[i]:
                self.issue.add_to_labels(mandatory_list[i] + "/none")
