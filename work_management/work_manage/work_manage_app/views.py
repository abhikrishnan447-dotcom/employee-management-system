from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import redirect, render

from .models import Register


# Home Page
def index(request):
    return render(request, "index.html")


# Employee registration
def register(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        profile_photo = request.FILES.get("profile_photo")
        email = request.POST.get("email", "").strip().lower()
        phone = request.POST.get("phone", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if not name or len(name) < 3:
            messages.error(request, "Please enter a valid name.")
            return render(request, "register.html")

        if not phone.isdigit() or len(phone) != 10:
            messages.error(request, "Please enter a valid 10-digit phone number.")
            return render(request, "register.html")

        if Register.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, "register.html")

        if len(password) < 8:
            messages.error(request, "Password must contain at least 8 characters.")
            return render(request, "register.html")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "register.html")

        if profile_photo and profile_photo.size > 2 * 1024 * 1024:
            messages.error(request, "Profile photo must be smaller than 2 MB.")
            return render(request, "register.html")

        Register.objects.create(
            name=name,
            email=email,
            phone=phone,
            password=make_password(password),
            profile_photo=profile_photo,
        )

        messages.success(request, "Registration successful. Please login.")
        return redirect("login")

    return render(request, "register.html")


# Employee login
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")

        try:
            user = Register.objects.get(email=email)
        except Register.DoesNotExist:
            messages.error(request, "Invalid email or password.")
            return redirect("login")

        if user.status != "Active":
            messages.error(request, "Your account is inactive. Please contact the administrator.")
            return redirect("login")

        if check_password(password, user.password):
            request.session["user_id"] = user.id
            request.session["email"] = user.email
            return redirect("home")

        messages.error(request, "Invalid email or password.")
        return redirect("login")

    return render(request, "login.html")


# Employee home
def home(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    try:
        user = Register.objects.get(id=user_id)
    except Register.DoesNotExist:
        request.session.flush()
        return redirect("login")

    return render(request, "home.html", {"user": user})


# Employee logout
def logout(request):
    request.session.flush()
    messages.success(request, "Logout successful.")
    return redirect("index")


# Employee dashboard
def dashboard(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    try:
        user = Register.objects.get(id=user_id)
    except Register.DoesNotExist:
        request.session.flush()
        return redirect("login")

    return render(request, "dashboard.html", {"user": user})


# Admin login
# Set these environment variables in a local .env/server environment.
import os

ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")


def adminlogin(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")

        if ADMIN_EMAIL and ADMIN_PASSWORD and email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            request.session["admin"] = email
            return redirect("admin_dash")

        messages.error(request, "Invalid admin login.")

    return render(request, "adminlogin.html")


# Admin dashboard
def admin_dash(request):
    if not request.session.get("admin"):
        return redirect("adminlogin")

    total_employees = Register.objects.count()
    active_employees = Register.objects.filter(status="Active").count()
    inactive_employees = Register.objects.filter(status="Inactive").count()

    context = {
        "total_employees": total_employees,
        "active_employees": active_employees,
        "inactive_employees": inactive_employees,
    }

    return render(request, "admin_dash.html", context)


# Admin logout
def adminlogout(request):
    request.session.pop("admin", None)
    return redirect("adminlogin")
