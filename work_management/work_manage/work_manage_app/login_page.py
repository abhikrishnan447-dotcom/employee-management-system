from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import redirect, render

from .models import Register


# ============================================================
# EMPLOYEE LOGIN - CLEAN LOGIN PAGE
# ============================================================
def employee_login(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        user = Register.objects.filter(email=email).first()

        if user and user.status == "Active":
            authenticated = check_password(password, user.password)

            # OLD PLAIN-TEXT PASSWORD - CONVERT ON SUCCESSFUL LOGIN
            if not authenticated and user.password == password:
                user.password = make_password(password)
                user.save(update_fields=["password"])
                authenticated = True

            if authenticated:
                request.session["user_id"] = user.id
                request.session["email"] = user.email
                return redirect("home")

        messages.error(request, "Invalid email or password.")

    return render(request, "login_fixed.html")
