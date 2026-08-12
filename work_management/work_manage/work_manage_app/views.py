from datetime import date
import os

from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.core.mail import send_mail
from django.db.models import Count, Avg, Q
from django.shortcuts import get_object_or_404, redirect, render

from .models import Department, EmployeeDepartment, ExtensionRequest, Message, Notification, ProgressUpdate, Register, Task, TaskFile


def index(request): return render(request, "index.html")

def register(request):
    if request.method == "POST":
        name=request.POST.get("name","").strip(); profile_photo=request.FILES.get("profile_photo"); email=request.POST.get("email","").strip().lower(); phone=request.POST.get("phone","").strip(); designation=request.POST.get("designation","").strip(); password=request.POST.get("password",""); confirm_password=request.POST.get("confirm_password",""); department_id=request.POST.get("department") or None
        if not name or len(name)<3: messages.error(request,"Please enter a valid name.")
        elif not phone.isdigit() or len(phone)!=10: messages.error(request,"Please enter a valid 10-digit phone number.")
        elif Register.objects.filter(email=email).exists(): messages.error(request,"Email already exists.")
        elif len(password)<8: messages.error(request,"Password must contain at least 8 characters.")
        elif password!=confirm_password: messages.error(request,"Passwords do not match.")
        elif profile_photo and profile_photo.size>2*1024*1024: messages.error(request,"Profile photo must be smaller than 2 MB.")
        else:
            employee=Register.objects.create(name=name,email=email,phone=phone,designation=designation,password=make_password(password),profile_photo=profile_photo,department_id=department_id)
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

def logout(request): request.session.flush(); return redirect("index")

def current_employee(request):
    user_id=request.session.get("user_id"); return Register.objects.filter(id=user_id,status="Active").first() if user_id else None

def home(request):
    user=current_employee(request)
    if not user: return redirect("login")
    return render(request,"home.html",{"user":user})

def employee_task_queryset(user):
    return Task.objects.filter(Q(assigned_employees=user) | Q(assigned_employees__isnull=True, assigned_to=user)).distinct()

ADMIN_EMAIL = 'admin@gamil.com'
ADMIN_PASSWORD = 'admin@123'

def adminlogin(request):
    if request.method=="POST":
        email=request.POST.get("email","").strip().lower(); password=request.POST.get("password","")
        if ADMIN_EMAIL and ADMIN_PASSWORD and email==ADMIN_EMAIL and password==ADMIN_PASSWORD:
            request.session["admin"]=email; return redirect("admin_dash")
        messages.error(request,"Invalid admin login or administrator credentials are not configured.")
    return render(request,"adminlogin.html")

def is_admin(request): return bool(request.session.get("admin"))

def admin_dash(request):
    if not is_admin(request): return redirect("adminlogin")
    return render(request,"admin/dashboard.html",{"total_employees":Register.objects.count(),"active_employees":Register.objects.filter(status="Active").count(),"total_tasks":Task.objects.count(),"pending_extensions":ExtensionRequest.objects.filter(status="Pending").count(),"completed_tasks":Task.objects.filter(status="Completed").count(),"employees":Register.objects.all().select_related("department").order_by("name")[:8]})

def adminlogout(request): request.session.flush(); return redirect("index")

def employee_management(request):
    if not is_admin(request): return redirect("adminlogin")
    return render(request,"admin/employees.html",{"employees":Register.objects.all().order_by("name"),"departments":Department.objects.all()})

def employee_edit(request,employee_id):
    if not is_admin(request): return redirect("adminlogin")
    employee=get_object_or_404(Register,id=employee_id)
    if request.method=="POST":
        employee.name=request.POST.get("name",employee.name).strip(); employee.phone=request.POST.get("phone",employee.phone).strip(); employee.status=request.POST.get("status",employee.status); department_id=request.POST.get("department") or None; employee.department_id=department_id; employee.designation=request.POST.get("designation",employee.designation).strip(); employee.save(); EmployeeDepartment.objects.update_or_create(employee=employee,defaults={"department_id":department_id}); messages.success(request,"Employee updated."); return redirect("employee_management")
    return render(request,"admin/employee_form.html",{"employee":employee,"departments":Department.objects.all(),"assignment":getattr(employee,"department_assignment",None)})

# Remaining view functions continue unchanged in the existing project.
