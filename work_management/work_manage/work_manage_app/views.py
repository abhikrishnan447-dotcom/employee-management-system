from datetime import date
import os

from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Count, Avg, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str

from .models import Department, EmployeeDepartment, ExtensionRequest, Message, Notification, ProgressUpdate, Register, Task, TaskFile


ADMIN_EMAIL = "admin@gmail.com"
ADMIN_PASSWORD = "admin@123"


def index(request): return render(request, "index.html")


def register(request):
    if request.method == "POST":
        name=request.POST.get("name","").strip(); profile_photo=request.FILES.get("profile_photo"); email=request.POST.get("email","").strip().lower(); phone=request.POST.get("phone","").strip(); password=request.POST.get("password",""); confirm_password=request.POST.get("confirm_password",""); department_id=request.POST.get("department") or None
        if not name or len(name)<3: messages.error(request,"Please enter a valid name.")
        elif not phone.isdigit() or len(phone)!=10: messages.error(request,"Please enter a valid 10-digit phone number.")
        elif Register.objects.filter(email=email).exists(): messages.error(request,"Email already exists.")
        elif len(password)<8: messages.error(request,"Password must contain at least 8 characters.")
        elif password!=confirm_password: messages.error(request,"Passwords do not match.")
        elif profile_photo and profile_photo.size>2*1024*1024: messages.error(request,"Profile photo must be smaller than 2 MB.")
        else:
            employee=Register.objects.create(name=name,email=email,phone=phone,password=make_password(password),profile_photo=profile_photo,department_id=department_id)
            if department_id: EmployeeDepartment.objects.update_or_create(employee=employee,defaults={"department_id":department_id})
            messages.success(request,"Registration successful. Please login."); return redirect("login")
    return render(request,"register.html",{"departments":Department.objects.all()})


def registration_departments(request): return render(request,"registration_departments.html",{"departments":Department.objects.all()})


def login_view(request):
    if request.method=="POST":
        email=request.POST.get("email","").strip().lower(); password=request.POST.get("password",""); user=Register.objects.filter(email=email).first()
        if user and user.status=="Active":
            authenticated=check_password(password,user.password)
            if not authenticated and user.password==password: user.password=make_password(password); user.save(update_fields=["password"]); authenticated=True
            if authenticated: request.session["user_id"]=user.id; request.session["email"]=user.email; return redirect("home")
        messages.error(request,"Invalid email or password.")
    return render(request,"login.html")


def forgot_password(request):
    if request.method=="POST":
        email=request.POST.get("email","").strip().lower(); user=Register.objects.filter(email=email).first()
        if user:
            uid=urlsafe_base64_encode(force_bytes(user.pk)); token=default_token_generator.make_token(user); reset_url=request.build_absolute_uri(f"/reset-password/{uid}/{token}/")
            try: send_mail("WorkSphere - Reset your password",f"Hello {user.name},\n\nUse the link below to create a new password:\n\n{reset_url}",None,[user.email],fail_silently=False); messages.success(request,"A password reset link has been sent to your registered email address.")
            except Exception: messages.error(request,"Unable to send the reset email. Please check the email server configuration.")
        else: messages.error(request,"No employee account was found with that email address.")
        return redirect("forgot_password")
    return render(request,"forgot_password.html")


def reset_password(request,uidb64,token):
    try: user=Register.objects.get(pk=force_str(urlsafe_base64_decode(uidb64)))
    except (TypeError,ValueError,OverflowError,Register.DoesNotExist): user=None
    if not user or not default_token_generator.check_token(user,token): messages.error(request,"This password reset link is invalid or has expired."); return redirect("forgot_password")
    if request.method=="POST":
        password=request.POST.get("password",""); confirm_password=request.POST.get("confirm_password","")
        if len(password)<8: messages.error(request,"Passwords must contain at least 8 characters.")
        elif password!=confirm_password: messages.error(request,"Passwords do not match.")
        else: user.password=make_password(password); user.save(update_fields=["password"]); messages.success(request,"Password changed successfully. You can now login."); return redirect("login")
    return render(request,"reset_password.html",{"email":user.email})


def logout(request): request.session.flush(); return redirect("index")

def current_employee(request):
    user_id=request.session.get("user_id"); return Register.objects.filter(id=user_id,status="Active").first() if user_id else None

def home(request):
    user=current_employee(request)
    if not user: return redirect("login")
    return render(request,"home.html",{"user":user})


def employee_task_queryset(user):
    return Task.objects.filter(Q(assigned_employees=user) | Q(assigned_employees__isnull=True, assigned_to=user)).distinct()


def dashboard(request):
    user=current_employee(request)
    if not user: return redirect("login")
    tasks=employee_task_queryset(user); task_rows=[]
    for task in tasks:
        extension=task.extension_requests.filter(employee=user).order_by("-created_at").first(); latest_update=task.updates.filter(employee=user).order_by("-created_at").first()
        task_rows.append({"task":task,"extension_status":extension.status if extension else "Not Requested","latest_progress":latest_update.progress if latest_update else task.progress})
    return render(request,"employee/dashboard.html",{"user":user,"tasks":tasks,"task_rows":task_rows,"pending":tasks.filter(status="Pending").count(),"progress":tasks.filter(status="In Progress").count(),"completed":tasks.filter(status="Completed").count()})


def adminlogin(request):
    if request.method=="POST":
        email=request.POST.get("email","").strip().lower(); password=request.POST.get("password","")
        if email == ADMIN_EMAIL.lower() and password == ADMIN_PASSWORD:
            request.session["admin"] = ADMIN_EMAIL
            return redirect("admin_dash")
        messages.error(request,"Invalid admin email or password.")
    return render(request,"adminlogin.html")


def is_admin(request): return bool(request.session.get("admin"))

def admin_dash(request):
    if not is_admin(request): return redirect("adminlogin")
    return render(request,"admin/dashboard.html",{"total_employees":Register.objects.count(),"active_employees":Register.objects.filter(status="Active").count(),"total_tasks":Task.objects.count(),"pending_extensions":ExtensionRequest.objects.filter(status="Pending").count(),"completed_tasks":Task.objects.filter(status="Completed").count(),"employees":Register.objects.all().select_related("department").order_by("name")[:8]})

def adminlogout(request): request.session.flush(); return redirect("index")

def employee_management(request):
    if not is_admin(request): return redirect("adminlogin")
    return render(request,"admin/employees_v2.html",{"employees":Register.objects.all().order_by("name"),"departments":Department.objects.all()})

# Remaining project views are unchanged.
