from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt

from .models import VisitorMessage


def visitor_message_submit(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request method."}, status=405)

    name = request.POST.get("name", "").strip()
    email = request.POST.get("email", "").strip().lower()
    message = request.POST.get("message", "").strip()

    if not name or len(name) < 2:
        return JsonResponse({"success": False, "message": "Please enter your name."}, status=400)
    if not email or "@" not in email:
        return JsonResponse({"success": False, "message": "Please enter a valid email address."}, status=400)
    if not message or len(message) < 3:
        return JsonResponse({"success": False, "message": "Please enter a message."}, status=400)

    VisitorMessage.objects.create(name=name, email=email, message=message)
    return JsonResponse({"success": True, "message": "Thanks! Your message has been sent successfully."})


def admin_visitor_messages(request):
    if not request.session.get("admin"):
        return redirect("adminlogin")

    if request.method == "POST":
        action = request.POST.get("action")
        message_id = request.POST.get("message_id")
        if action == "delete" and message_id:
            item = get_object_or_404(VisitorMessage, id=message_id)
            item.delete()
            messages.success(request, "Visitor message deleted.")
        elif action == "clear":
            VisitorMessage.objects.all().delete()
            messages.success(request, "All visitor messages cleared.")
        return redirect("admin_visitor_messages")

    items = VisitorMessage.objects.all()
    items.filter(is_read=False).update(is_read=True)
    return render(request, "admin/visitor_messages.html", {
        "visitor_messages": items,
        "visitor_message_count": VisitorMessage.objects.filter(is_read=False).count(),
    })
