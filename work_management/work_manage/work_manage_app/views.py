from django.shortcuts import render

from .views_legacy import *


def index(request):
    return render(request, "landing/index.html")


def register(request):
    if request.method == "POST":
        return register_fixed(request)
    return render(request, "employee/register.html", {"departments": Department.objects.all()})


def login_view(request):
    return employee_login(request)


def home(request):
    user = current_employee(request)
    if not user:
        return redirect("login")
    return render(request, "landing/home.html", {"user": user})


def adminlogin(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        if ADMIN_EMAIL and ADMIN_PASSWORD and email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            request.session["admin"] = email
            return redirect("admin_dash")
        messages.error(request, "Invalid admin login or administrator credentials are not configured.")
    return render(request, "admin/adminlogin.html")


def register_fixed(request):
    if request.method == "POST":
        return views_legacy_register_fixed(request)
    return render(request, "employee/register.html", {"departments": Department.objects.all()})


def employee_login(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        user = Register.objects.filter(email=email).first()
        if user and user.status == "Active":
            authenticated = check_password(password, user.password)
            if not authenticated and user.password == password:
                user.password = make_password(password)
                user.save(update_fields=["password"])
                authenticated = True
            if authenticated:
                request.session["user_id"] = user.id
                request.session["email"] = user.email
                return redirect("home")
        messages.error(request, "Invalid email or password.")
    return render(request, "employee/login.html")


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
    return render(request, "employee/forgot_password.html")


# Keep the original register_fixed implementation available under a private alias.
from .views_legacy import register_fixed as views_legacy_register_fixed
