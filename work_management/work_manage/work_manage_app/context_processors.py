from .models import ExtensionRequest, Message, Notification, Register


# ============================================================
# GLOBAL TEMPLATE BADGES / NOTIFICATION COUNTERS
# ============================================================
def admin_badges(request):
    """Provide unread notification/message counters to templates."""
    employee = None
    user_id = request.session.get("user_id")
    if user_id:
        employee = Register.objects.filter(id=user_id, status="Active").first()

    # EMPLOYEE - UNREAD COUNTS
    employee_notification_count = (
        employee.notifications.filter(is_read=False).count() if employee else 0
    )
    employee_message_count = (
        Message.objects.filter(recipient=employee, is_read=False).count()
        if employee else 0
    )

    # NON-ADMIN USER
    if not request.session.get("admin"):
        return {
            "admin_notification_count": 0,
            "admin_message_count": 0,
            "admin_extension_count": 0,
            "employee_notification_count": employee_notification_count,
            "employee_message_count": employee_message_count,
        }

    # ADMIN - UNREAD COUNTS
    return {
        "admin_notification_count": Notification.objects.filter(is_read=False).count(),
        "admin_message_count": Message.objects.filter(
            is_admin_recipient=True, is_read=False
        ).count(),
        "admin_extension_count": ExtensionRequest.objects.filter(status="Pending").count(),
        "employee_notification_count": employee_notification_count,
        "employee_message_count": employee_message_count,
    }
