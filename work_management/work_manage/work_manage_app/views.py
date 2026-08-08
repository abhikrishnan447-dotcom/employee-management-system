from datetime import date
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Count, Avg, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from .models import Department, EmployeeDepartment, ExtensionRequest, Message, Notification, ProgressUpdate, Register, Task, TaskFile


def index(request): return render(request, "index.html")
# ... existing views unchanged ...

# Employee message inbox: messages remain until the employee uses Clear Messages.
def clear_messages(request):
    user=current_employee(request)
    if not user: return redirect("login")
    if request.method=="POST":
        Message.objects.filter(recipient_id=user.id).delete()
        messages.success(request,"Inbox messages cleared.")
    return redirect("messages")

# Individual inbox-message deletion is intentionally disabled; messages are
# removed only through the Clear Messages action.

def profile(request):
    user=current_employee(request)
    if not user: return redirect("login")
    if request.method=="POST":
        user.name=request.POST.get("name",user.name).strip(); user.phone=request.POST.get("phone",user.phone).strip()
        if request.FILES.get("profile_photo"): user.profile_photo=request.FILES["profile_photo"]
        user.save(); messages.success(request,"Profile updated successfully.")
    return render(request,"employee/profile.html",{"user":user})

def settings_view(request):
    user=current_employee(request)
    if not user: return redirect("login")
    if request.method=="POST":
        new_password=request.POST.get("new_password","")
        if len(new_password)>=8: user.password=make_password(new_password); user.save(update_fields=["password"]); messages.success(request,"Password updated.")
    return render(request,"employee/settings.html",{"user":user})
