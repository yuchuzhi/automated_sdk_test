from redminelib import Redmine
from unittest import TestCase


class TestRedmine(TestCase):
    def test_redmine_connect(self):
        redmine = Redmine("http://localhost/redmine/", username="fly", password="Happy123")
        project = redmine.project.get("auto-build")
        print(dir(redmine.issue))
        issues = redmine.issue.get(1)
        print(issues.__dict__)
        print(list(issues.project))

        # issues1 = redmine.issue.filter(project_id="hello-wrold-build-issue")

