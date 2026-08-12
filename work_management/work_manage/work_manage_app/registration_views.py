import re

from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.shortcuts import redirect, render

from .models import Department, EmployeeDepartment, Register


PASSWORD_PATTERN = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z\d]).{8,}$")


def register(request):
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
        elif not PASSWORD_PATTERN.fullmatch(password):
            messages.error(
                request,
                "Password must be at least 8 characters and include one uppercase letter, one lowercase letter, one number, and one special character.",
            )
        elif password != confirm_password:
            messages.error(request, "Passwords do not match.")
        elif profile_photo and profile_photo.size > 2 * 1024 * 1024:
            messages.error(request, "Profile photo must be smaller than 2 MB.")
        else:
            employee = Register.objects.create(
                name=name,
                email=email,
                phone=phone,
                designation=designation,
                password=make_password(password),
                profile_photo=profile_photo,
                department_id=department_id,
            )

            if department_id:
                EmployeeDepartment.objects.update_or_create(
                    employee=employee,
                    defaults={"department_id": department_id},
                )

            messages.success(request, "Registration successful. Please login.")
            return redirect("login")

    return render(request, "register.html", {"departments": Department.objects.all()})
