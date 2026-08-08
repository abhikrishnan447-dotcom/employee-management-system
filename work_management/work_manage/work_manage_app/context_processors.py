from .models import Message, Notification


def admin_badges(request):
    """Provide unread admin-side counters to every template."""
    if not request.session.get("admin"):
        return {"admin_notification_count": 0, "admin_message_count": 0}

    return {
        "admin_notification_count": Notification.objects.filter(is_read=False).count(),
        "admin_message_count": Message.objects.filter(is_admin_recipient=True, is_read=False).count(),
    }
