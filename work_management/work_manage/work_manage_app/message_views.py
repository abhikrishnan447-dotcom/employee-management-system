from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Message, Notification, Register
from .views import current_employee, is_admin


def _visible_after(request, session_key):
    value = request.session.get(session_key)
    if not value:
        return None
    try:
        return timezone.datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def _save_clear_time(request, session_key):
    request.session[session_key] = timezone.now().isoformat()
    request.session.modified = True


def messages_view(request):
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
            recipient = get_object_or_404(Register, id=recipient_id, status="Active")
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

    cleared_at = _visible_after(request, "employee_messages_cleared_at")
    received_qs = Message.objects.filter(recipient_id=user.id).select_related("sender", "recipient")
    sent_qs = Message.objects.filter(sender_id=user.id).select_related("sender", "recipient")
    if cleared_at:
        received_qs = received_qs.filter(created_at__gt=cleared_at)
        sent_qs = sent_qs.filter(created_at__gt=cleared_at)

    received = list(received_qs.order_by("-created_at"))
    sent = list(sent_qs.order_by("-created_at"))
    Message.objects.filter(recipient_id=user.id, is_read=False).update(is_read=True)

    return render(
        request,
        "employee/messages.html",
        {
            "user": user,
            "received": received,
            "sent": sent,
            "employees": Register.objects.filter(status="Active").exclude(id=user.id),
        },
    )


def clear_messages(request):
    user = current_employee(request)
    if not user:
        return redirect("login")
    if request.method == "POST":
        _save_clear_time(request, "employee_messages_cleared_at")
        messages.success(request, "Your messages were cleared from your dashboard.")
    return redirect("messages")


def admin_messages(request):
    if not is_admin(request):
        return redirect("adminlogin")

    if request.method == "POST":
        recipient = get_object_or_404(Register, id=request.POST.get("recipient"), status="Active")
        subject = request.POST.get("subject", "").strip()
        body = request.POST.get("body", "").strip()
        if not subject or not body:
            messages.error(request, "Please enter a subject and message.")
            return redirect("admin_messages")

        Message.objects.create(
            sender=None,
            recipient=recipient,
            subject=subject,
            body=body,
            is_admin_sender=True,
        )
        Notification.objects.create(
            recipient=recipient,
            title="New message from Admin",
            message="The administrator sent you a new message.",
        )
        if recipient.email:
            try:
                send_mail(
                    "WorkSphere - Message from Admin",
                    f"Hello {recipient.name},\n\n{body}\n\nPlease login to WorkSphere to reply.",
                    None,
                    [recipient.email],
                    fail_silently=False,
                )
            except Exception:
                pass
        messages.success(request, "Message sent to employee.")
        return redirect("admin_messages")

    cleared_at = _visible_after(request, "admin_messages_cleared_at")
    items = Message.objects.filter(
        is_admin_recipient=True
    ) | Message.objects.filter(is_admin_sender=True)
    items = items.select_related("sender", "recipient").order_by("-created_at")
    if cleared_at:
        items = items.filter(created_at__gt=cleared_at)

    Message.objects.filter(is_admin_recipient=True, is_read=False).update(is_read=True)
    return render(
        request,
        "admin/messages.html",
        {
            "messages_list": items,
            "employees": Register.objects.filter(status="Active"),
        },
    )


def admin_clear_messages(request):
    if not is_admin(request):
        return redirect("adminlogin")
    if request.method == "POST":
        _save_clear_time(request, "admin_messages_cleared_at")
        messages.success(request, "Administrator messages were cleared from the admin dashboard.")
    return redirect("admin_messages")


def admin_message_reply(request, message_id):
    if not is_admin(request):
        return redirect("admin_messages")
    original = get_object_or_404(Message, id=message_id)
    recipient = original.sender if original.sender_id else original.recipient
    if not recipient:
        return redirect("admin_messages")
    if request.method == "POST":
        subject = request.POST.get("subject", f"Re: {original.subject}").strip()
        body = request.POST.get("body", "").strip()
        if body:
            Message.objects.create(
                sender=None,
                recipient=recipient,
                subject=subject,
                body=body,
                is_admin_sender=True,
            )
            Notification.objects.create(
                recipient=recipient,
                title="Admin replied",
                message=f"Admin replied to your message: {subject}",
            )
            messages.success(request, "Reply sent to employee.")
    return redirect("admin_messages")
