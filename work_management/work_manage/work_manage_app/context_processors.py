from .models import ExtensionRequest, Message, Notification


def admin_badges(request):
    """Provide employee and admin notification/message counters to every template."""
    employee = None
    user_id = request.session.get("user_id")
    if user_id:
        # Import locally to avoid making the app import this model during startup.
        from .models import Register
        employee = Register.objects.filter(id=user_id, status="Active").first()

    employee_notification_count = employee.notifications.filter(is_read=False).count() if employee else 0
    employee_message_count = (
        Message.objects.filter(
            Q_placeholder if False else Message.objects.none()
        ).count()
        if False else 0
    )
    if employee:
        employee_message_count = Message.objects.filter(
            recipient=employee,
            is_read=False,
        ).count()

    if not request.session.get("admin"):
        return {
            "admin_notification_count": 0,
            "admin_message_count": 0,
            "admin_extension_count": 0,
            "employee_notification_count": employee_notification_count,
            "employee_message_count": employee_message_count,
        }

    return {
        "admin_notification_count": Notification.objects.filter(is_read=False).count(),
        "admin_message_count": Message.objects.filter(is_admin_recipient=True, is_read=False).count(),
        "admin_extension_count": ExtensionRequest.objects.filter(status="Pending").count(),
        "employee_notification_count": employee_notification_count,
        "employee_message_count": employee_message_count,
    }
