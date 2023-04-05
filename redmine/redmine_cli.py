from redminelib import Redmine

# redmine = Redmine("http://localhost/redmine/", username="fly", passwd="Happy123")
# print(redmine.__dict__)
# print(dir(redmine.project))
# project = redmine.project.get("auto-build")
# print(dir(redmine.issue))
# issues = redmine.issue.get(1)
# print(issues.url)
# print(list(issues.project))

# issues1 = redmine.issue.filter(project_id="hello-wrold-build-issue")


class RedmineCli(object):
    def __init__(self):
        self.name = None
        self.redmine = None

    def connect(self, url, username, password):
        self.redmine = Redmine(url, username=username, password=password)

    def create_project(self, name, identifier, **kwargs):
        """create a project.
        Args:
            name (string) – (required). Project name.
            identifier (string) – (required). Project identifier.
            description (string) – (optional). Project description.
            homepage (string) – (optional). Project homepage url.
            is_public (bool) – (optional). Whether project is public.
            parent_id (int) – (optional). Project’s parent project id.
            inherit_members (bool) – (optional). Whether to inherit parent project’s members.
            tracker_ids (list) – (optional). The ids of trackers for this project.
            issue_custom_field_ids (list) – (optional). The ids of issue custom fields for this project.
            custom_fields (list) – (optional). Custom fields as [{‘id’: 1, ‘value’: ‘foo’}].
            enabled_module_names (list) – (optional). The names of enabled modules for this project (requires Redmine >= 2.6.0).
        """
        try:
            project = self.redmine.project.new()
            project.name = name
            project.identifier = identifier
            project.description = kwargs.get("description", "")
            project.is_public = kwargs.get("is_public", True)
            project.parent_id = kwargs.get("parent_id", None)
            project.inherit_members = kwargs.get("inherit_members", True)
            project.custom_fields = kwargs.get("custom_fields", [])
            project.homepage = kwargs.get("homepage", None)
            project.tracker_ids = kwargs.get("tracker_ids", [])
            project.issue_custom_field_ids = kwargs.get("issue_custom_field_ids", [])
            project.enabled_module_names = kwargs.get("enabled_module_names", [])

            project.save()
        except Exception as e:
            print(repr(e))

    def create_issue(self, project_id, subject, **kwargs):
        """create a issue.

        Args:
            project_id (int or string) – (required). Id or identifier of issue’s project.
            subject (string) – (required). Issue subject.
            tracker_id (int) – (optional). Issue tracker id.
            description (string) – (optional). Issue description.
            status_id (int) – (optional). Issue status id.
            priority_id (int) – (optional). Issue priority id.
            category_id (int) – (optional). Issue category id.
            fixed_version_id (int) – (optional). Issue version id.
            is_private (bool) – (optional). Whether issue is private.
            assigned_to_id (int) – (optional). Issue will be assigned to this user id.
            watcher_user_ids (list) – (optional). User ids watching this issue.
            parent_issue_id (int) – (optional). Parent issue id.
            start_date (string or date object) – (optional). Issue start date.
            due_date (string or date object) – (optional). Issue end date.
            estimated_hours (int) – (optional). Issue estimated hours.
            done_ratio (int) – (optional). Issue done ratio.
            custom_fields (list) – (optional). Custom fields as [{‘id’: 1, ‘value’: ‘foo’}].
            uploads (list) – (optional). Uploads as [{'': ''}, ...], accepted keys are:
            path (required). Absolute file path or file-like object that should be uploaded.
            filename (optional). Name of the file after upload.
            description (optional). Description of the file.
            content_type (optional). Content type of the file.
        """
        try:
            self.redmine.issue.create(
                project_id=project_id,
                subject=subject,
                assigned_to_id=kwargs.get("assigned_to_id", 1),
                description=kwargs.get("description", "it is a bug"),
                tracker_id=kwargs.get("tracker_id", 1),
                status_id=kwargs.get("status_id", 1),
                priority_id=kwargs.get("priority_id", 2),
                category_id=kwargs.get("category_id", None),
                fixed_version_id=kwargs.get("fixed_version_id", None),
                is_private=kwargs.get("is_private", False),
                watcher_user_ids=kwargs.get("watcher_user_ids", None),
                parent_issue_id=kwargs.get("parent_issue_id", None),
                start_date=kwargs.get("start_date", None),
                due_date=kwargs.get("due_date", None),
                estimated_hours=kwargs.get("estimated_hours", None),
                done_ratio=kwargs.get("done_ratio", None),
                custom_fields=kwargs.get("custom_fields", []),
                uploads=kwargs.get("uploads", [])
            )

        except Exception as e:
            print(repr(e))

if __name__ == "__main__":
    redmine_cli = RedmineCli()
    redmine_cli.connect("http://192.168.0.202/", username="admin", password="Happy123")
    #redmine_cli.create_issue(1, "issue")

