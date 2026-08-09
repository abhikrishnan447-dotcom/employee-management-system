from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .models import Message, Notification, Register
from .views import current_employee


# ============================================================
# EMPLOYEE MESSAGES - SHOW SENT + RECEIVED IN THE SAME INBOX
# ============================================================
def messages_view_fixed(request):
    user = current_employee(request)
    if not user:
        return redirect("login")

    if request.method == "POST":
        recipient_id = request.POST.get("recipient")
        subject = request.POST.get("subject", "").strip()
        body = request.POST.get("body", "").strip()

        if not subject or not body:
            messages.error(request, "Please enter a subject and message.")
            return redirect("messages")

        if recipient_id == "admin":
            Message.objects.create(
                sender=user,
                recipient=None,
                subject=subject,
                body=body,
                is_admin_recipient=True,
                is_read=False,
            )
            messages.success(request, "Message sent to Admin.")
        else:
            recipient = get_object_or_404(
                Register,
                id=recipient_id,
                status="Active",
            )

            if recipient.id == user.id:
                messages.error(request, "You cannot send a message to yourself.")
                return redirect("messages")

            Message.objects.create(
                sender=user,
                recipient=recipient,
                subject=subject,
                body=body,
                is_read=False,
            )
            Notification.objects.create(
                recipient=recipient,
                title="New message",
                message=f"New message from {user.name}.",
            )
            messages.success(request, f"Message sent to {recipient.name}.")

        return redirect("messages")

    # Inbox contains both received messages and messages sent by the employee.
    # This makes a newly sent message immediately visible in the same Inbox.
    inbox_qs = (
        Message.objects
        .filter(Q(recipient=user) | Q(sender=user))
        .select_related("sender", "recipient")
        .order_by("-created_at")
    )

    # Only incoming unread messages are marked as read.
    Message.objects.filter(recipient=user, is_read=False).update(is_read=True)

    return render(
        request,
        "employee/messages.html",
        {
            "user": user,
            "received": inbox_qs,
            "employees": Register.objects.filter(status="Active").exclude(id=user.id),
        },
    )
