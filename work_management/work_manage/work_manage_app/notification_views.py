from django.contrib import messages
from django.shortcuts import redirect, render

from .models import Notification
from .views import current_employee, is_admin


def notifications(request):
    """Show only notifications visible to the logged-in employee."""
    user = current_employee(request)
    if not user:
        return redirect("login")

    items = user.notifications.filter(employee_cleared=False).order_by("-created_at")
    items.filter(is_read=False).update(is_read=True)
    return render(
        request,
        "employee/notifications.html",
        {"user": user, "notifications": items},
    )


def clear_notifications(request):
    """Clear notifications only for this employee; keep them visible to admin."""
    user = current_employee(request)
    if not user:
        return redirect("login")

    if request.method == "POST":
        user.notifications.filter(employee_cleared=False).update(employee_cleared=True)
        messages.success(request, "Notifications cleared.")
    return redirect("notifications")


def admin_notifications(request):
    """Show only notifications that have not been cleared by the admin."""
    if not is_admin(request):
        return redirect("adminlogin")

    items = Notification.objects.filter(admin_cleared=False).select_related("recipient").order_by("-created_at")
    items.filter(is_read=False).update(is_read=True)
    return render(request, "admin/notifications.html", {"notifications": items})


def admin_clear_notifications(request):
    """Clear notifications only from the admin view; keep employee copies."""
    if not is_admin(request):
        return redirect("adminlogin")

    if request.method == "POST":
        Notification.objects.filter(admin_cleared=False).update(admin_cleared=True)
        messages.success(request, "Administrator notifications cleared.")
    return redirect("admin_notifications")
