from django.apps import AppConfig


# ==============================
# WORK MANAGE APP CONFIGURATION
# ==============================
class WorkManageAppConfig(AppConfig):
    name = 'work_manage_app'

    def ready(self):
        # Replace the old global-delete message handlers with the independent
        # employee/admin dashboard handlers from message_views.py.
        from . import views, message_views

        views.messages_view_fixed = message_views.messages_view
        views.clear_messages = message_views.clear_messages
        views.admin_messages = message_views.admin_messages
        views.admin_clear_messages = message_views.admin_clear_messages
        views.admin_message_reply = message_views.admin_message_reply
