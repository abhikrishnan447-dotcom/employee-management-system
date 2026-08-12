from django.contrib import messages
from django.shortcuts import redirect, render

from .models import Notification


def admin_notifications(request):
    if not request.session.get("admin"):
        return redirect("adminlogin")

    notifications_qs = Notification.objects.filter(recipient__isnull=True).order_by("-created_at")
    notifications_qs.filter(is_read=False).update(is_read=True)
    return render(request, "admin/notifications.html", {"notifications": notifications_qs})


def admin_clear_notifications(request):
    if not request.session.get("admin"):
        return redirect("adminlogin")

    if request.method == "POST":
        Notification.objects.filter(recipient__isnull=True).delete()
        messages.success(request, "Administrator notifications cleared.")
    return redirect("admin_notifications")
