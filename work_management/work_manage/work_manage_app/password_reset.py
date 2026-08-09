from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.shortcuts import redirect, render

from .models import Register


# ============================================================
# EMPLOYEE - SIMPLE WEBSITE PASSWORD RESET
# ============================================================
def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        user = Register.objects.filter(email=email, status="Active").first()

        if not user:
            messages.error(request, "No active employee account was found with that email address.")
        elif len(password) < 8:
            messages.error(request, "Password must contain at least 8 characters.")
        elif password != confirm_password:
            messages.error(request, "Passwords do not match.")
        else:
            user.password = make_password(password)
            user.save(update_fields=["password"])
            messages.success(request, "Password changed successfully. You can now login.")
            return redirect("login")

    return render(request, "forgot_password.html")
