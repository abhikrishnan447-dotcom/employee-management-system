import os
from datetime import date
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from .models import Department, EmployeeDepartment, ExtensionRequest, Message, Notification, ProgressUpdate, Register, Task

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
            try: send_mail("WorkSphere - Reset your password",f"Hello {user.name},\n\nUse the link below to create a new password:\n\n{reset_url}\n\nIf you did not request this, you can ignore this email.",None,[user.email],fail_silently=False); messages.success(request,"A password reset link has been sent to your registered email address.")
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
        if len(password)<8: messages.error(request,"Password must contain at least 8 characters.")
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
def dashboard(request):
    user=current_employee(request)
    if not user: return redirect("login")
    tasks=user.tasks.all()
    return render(request,"employee/dashboard.html",{"user":user,"tasks":tasks,"pending":tasks.filter(status="Pending").count(),"progress":tasks.filter(status="In Progress").count(),"completed":tasks.filter(status="Completed").count()})
ADMIN_EMAIL=os.environ.get("ADMIN_EMAIL",""); ADMIN_PASSWORD=os.environ.get("ADMIN_PASSWORD","")
def adminlogin(request):
    if request.method=="POST":
        email=request.POST.get("email","").strip().lower(); password=request.POST.get("password","")
        if ADMIN_EMAIL and ADMIN_PASSWORD and email==ADMIN_EMAIL.lower() and password==ADMIN_PASSWORD: request.session["admin"]=email; return redirect("admin_dash")
        messages.error(request,"Invalid admin login.")
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
        employee.name=request.POST.get("name",employee.name).strip(); employee.phone=request.POST.get("phone",employee.phone).strip(); employee.status=request.POST.get("status",employee.status); department_id=request.POST.get("department") or None; employee.department_id=department_id; employee.save(); EmployeeDepartment.objects.update_or_create(employee=employee,defaults={"department_id":department_id,"designation":request.POST.get("designation","")}); messages.success(request,"Employee updated."); return redirect("employee_management")
    return render(request,"admin/employee_form.html",{"employee":employee,"departments":Department.objects.all(),"assignment":getattr(employee,"department_assignment",None)})
def department_management(request):
    if not is_admin(request): return redirect("adminlogin")
    if request.method=="POST":
        name=request.POST.get("name","").strip(); description=request.POST.get("description","").strip()
        if name: Department.objects.get_or_create(name=name,defaults={"description":description})
        return redirect("department_management")
    return render(request,"admin/departments.html",{"departments":Department.objects.annotate(employee_count=Count("employees"))})
def department_delete(request,department_id):
    if not is_admin(request): return redirect("adminlogin")
    if request.method=="POST": get_object_or_404(Department,id=department_id).delete()
    return redirect("department_management")
def task_management(request):
    if not is_admin(request): return redirect("adminlogin")
    return render(request,"admin/tasks.html",{"tasks":Task.objects.select_related("assigned_to","department"),"employees":Register.objects.filter(status="Active"),"departments":Department.objects.all()})
def assign_task(request):
    if not is_admin(request): return redirect("adminlogin")
    if request.method=="POST":
        employee=get_object_or_404(Register,id=request.POST.get("assigned_to"),status="Active")
        task=Task.objects.create(title=request.POST.get("title","").strip(),description=request.POST.get("description","").strip(),assigned_to=employee,department_id=request.POST.get("department") or None,deadline=request.POST.get("deadline"),priority=request.POST.get("priority","Medium"))
        Notification.objects.create(recipient=employee,title="New task assigned",message=f"You have been assigned: {task.title}")
        try: sent=send_mail("WorkSphere - New Task Assigned",f"Hello {employee.name},\n\nA new task has been assigned to you.\n\nTask: {task.title}\nDescription: {task.description}\nPriority: {task.priority}\nDeadline: {task.deadline}\n\nPlease login to WorkSphere to view the task and update your progress.",None,[employee.email],fail_silently=False)
        except Exception: sent=0
        if sent: messages.success(request,f"Task assigned successfully. Email sent to {employee.email}.")
        else: messages.warning(request,"Task assigned, but email could not be sent. Configure EMAIL_HOST_USER and EMAIL_HOST_PASSWORD.")
    return redirect("task_management")
def extension_requests(request):
    if not is_admin(request): return redirect("adminlogin")
    return render(request,"admin/extensions.html",{"requests":ExtensionRequest.objects.select_related("task","employee")})
def extension_action(request,request_id,action):
    if not is_admin(request): return redirect("adminlogin")
    extension=get_object_or_404(ExtensionRequest,id=request_id)
    if request.method=="POST" and action in ("approve","reject"):
        extension.status="Approved" if action=="approve" else "Rejected"; extension.admin_note=request.POST.get("admin_note","").strip(); extension.save()
        if extension.status=="Approved": extension.task.deadline=extension.requested_deadline; extension.task.save(update_fields=["deadline"])
        Notification.objects.create(recipient=extension.employee,title=f"Extension {extension.status}",message=f"Your extension request for {extension.task.title} was {extension.status.lower()}.")
    return redirect("extension_requests")
def employee_tasks(request):
    user=current_employee(request)
    if not user: return redirect("login")
    return render(request,"employee/tasks.html",{"tasks":user.tasks.all()})
def task_detail(request,task_id):
    user=current_employee(request)
    if not user: return redirect("login")
    task=get_object_or_404(Task,id=task_id,assigned_to=user)
    return render(request,"employee/task_detail.html",{"task":task,"updates":task.updates.all(),"extensions":task.extension_requests.all()})
def progress_update(request,task_id):
    user=current_employee(request)
    if not user: return redirect("login")
    task=get_object_or_404(Task,id=task_id,assigned_to=user)
    if request.method=="POST":
        try: progress=max(0,min(100,int(request.POST.get("progress",0))))
        except (TypeError,ValueError): progress=0
        ProgressUpdate.objects.create(task=task,employee=user,progress=progress,note=request.POST.get("note","").strip()); task.progress=progress; task.status="Completed" if progress==100 else "In Progress" if progress>0 else "Pending"; task.save(update_fields=["progress","status"]); messages.success(request,"Progress updated successfully.")
    return redirect("progress_updates")
def progress_updates(request):
    user=current_employee(request)
    if not user: return redirect("login")
    return render(request,"employee/progress_updates.html",{"tasks":user.tasks.all(),"updates":user.progress_updates.select_related("task").all()})
def request_extension(request,task_id):
    user=current_employee(request)
    if not user: return redirect("login")
    task=get_object_or_404(Task,id=task_id,assigned_to=user)
    if request.method=="POST":
        requested_deadline=request.POST.get("requested_deadline"); reason=request.POST.get("reason","").strip()
        if requested_deadline and reason: ExtensionRequest.objects.create(task=task,employee=user,requested_deadline=requested_deadline,reason=reason); messages.success(request,"Extension request submitted successfully.")
        else: messages.error(request,"Please provide a new deadline and reason.")
    return redirect("extension_requests_employee")
def extension_requests_employee(request):
    user=current_employee(request)
    if not user: return redirect("login")
    return render(request,"employee/extension_requests.html",{"tasks":user.tasks.all(),"requests":user.extension_requests.select_related("task").all()})
def notifications(request):
    user=current_employee(request)
    if not user: return redirect("login")
    items=user.notifications.all(); items.filter(is_read=False).update(is_read=True); return render(request,"employee/notifications.html",{"notifications":items})
def messages_view(request):
    user=current_employee(request)
    if not user: return redirect("login")
    if request.method=="POST":
        recipient=get_object_or_404(Register,id=request.POST.get("recipient"),status="Active"); Message.objects.create(sender=user,recipient=recipient,subject=request.POST.get("subject",""),body=request.POST.get("body","")); Notification.objects.create(recipient=recipient,title="New message",message=f"New message from {user.name}."); return redirect("messages")
    return render(request,"employee/messages.html",{"received":user.received_messages.all(),"sent":user.sent_messages.all(),"employees":Register.objects.filter(status="Active").exclude(id=user.id)})
def profile(request):
    user=current_employee(request)
    if not user: return redirect("login")
    if request.method=="POST":
        user.name=request.POST.get("name",user.name).strip(); user.phone=request.POST.get("phone",user.phone).strip()
        if request.FILES.get("profile_photo"): user.profile_photo=request.FILES["profile_photo"]
        user.save()
    return render(request,"employee/profile.html",{"user":user})
def settings_view(request):
    user=current_employee(request)
    if not user: return redirect("login")
    if request.method=="POST":
        new_password=request.POST.get("new_password","")
        if len(new_password)>=8: user.password=make_password(new_password); user.save(update_fields=["password"]); messages.success(request,"Password updated.")
    return render(request,"employee/settings.html",{"user":user})
def reports(request):
    if not is_admin(request): return redirect("adminlogin")
    tasks=Task.objects.all(); return render(request,"admin/reports.html",{"total":tasks.count(),"pending":tasks.filter(status="Pending").count(),"progress":tasks.filter(status="In Progress").count(),"completed":tasks.filter(status="Completed").count(),"overdue":tasks.filter(deadline__lt=date.today()).exclude(status="Completed").count(),"by_department":Department.objects.annotate(task_count=Count("tasks"))})
def admin_notifications(request):
    if not is_admin(request): return redirect("adminlogin")
    return render(request,"admin/notifications.html",{"notifications":Notification.objects.select_related("recipient")})
def admin_messages(request):
    if not is_admin(request): return redirect("adminlogin")
    return render(request,"admin/messages.html",{"messages_list":Message.objects.select_related("sender","recipient")})
def admin_settings(request):
    if not is_admin(request): return redirect("adminlogin")
    return render(request,"admin/settings.html")
def admin_profile(request):
    if not is_admin(request): return redirect("adminlogin")
    return render(request,"admin/profile.html",{"admin_email":request.session.get("admin")})
