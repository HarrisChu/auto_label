import os
import json
from github import Github

from auto_label.issue import IssueProcessor


def main():
    token = os.environ["GH_PAT"]
    event = os.getenv("EVENT", None)
    event_name = os.getenv("EVENT_NAME", None)
    if event is None or event_name is None:
        print("No event found")
        exit(1)
    event_json = json.loads(event)
    gh = Github(token)

    processor = None
    if event_name == "issues":
        processor = IssueProcessor(gh, event_json)
    elif event_name == "pull_request":
        raise Exception("Not implemented yet")
    if processor is None:
        print("No processor found")
        exit(1)

    try:
        processor.run()
    except Exception as e:
        raise e


if __name__ == "__main__":
    main()
