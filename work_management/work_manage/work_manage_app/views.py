from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password

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
        name = request.POST.get("name", "").strip()
        profile_photo = request.FILES.get("profile_photo")
        email = request.POST.get("email", "").strip().lower()
        phone = request.POST.get("phone", "").strip()
        designation = request.POST.get("designation", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")
        department_id = request.POST.get("department") or None
        if not name or len(name) < 3:
            messages.error(request, "Please enter a valid name.")
        elif not phone.isdigit() or len(phone) != 10:
            messages.error(request, "Please enter a valid 10-digit phone number.")
        elif Register.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
        elif len(password) < 8 or not any(c.islower() for c in password) or not any(c.isupper() for c in password) or not any(c.isdigit() for c in password) or not any(not c.isalnum() for c in password):
            messages.error(request, "Password must be at least 8 characters and include one uppercase letter, one lowercase letter, one number, and one special character.")
        elif password != confirm_password:
            messages.error(request, "Passwords do not match.")
        elif profile_photo and profile_photo.size > 2 * 1024 * 1024:
            messages.error(request, "Profile photo must be smaller than 2 MB.")
        else:
            employee = Register.objects.create(name=name, email=email, phone=phone, designation=designation, password=make_password(password), profile_photo=profile_photo, department_id=department_id)
            if department_id:
                EmployeeDepartment.objects.update_or_create(employee=employee, defaults={"department_id": department_id})
            messages.success(request, "Registration successful. Please login.")
            return redirect("login")
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
