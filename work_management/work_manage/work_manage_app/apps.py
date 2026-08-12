from django.apps import AppConfig


class WorkManageAppConfig(AppConfig):
    name = "work_manage_app"

    def ready(self):
        # Import consolidated views so its signal receivers are registered once
        # after Django has populated the application registry.
        from . import views  # noqa: F401
