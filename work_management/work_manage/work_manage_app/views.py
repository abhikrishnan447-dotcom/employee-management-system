import re
from datetime import date

from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.core.mail import send_mail
from django.db.models import Avg, Count, Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt

from .models import (
    Department,
    EmployeeDepartment,
    ExtensionRequest,
    Message,
    Notification,
    ProgressUpdate,
    Register,
    Task,
    TaskFile,
    VisitorMessage,
)


# ==============================
# AUTH / COMMON HELPERS
# ==============================
ADMIN_EMAIL = "admin@gamil.com"
ADMIN_PASSWORD = "admin@123"
PASSWORD_PATTERN = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z\d]).{8,}$")


def current_employee(request):
    user_id = request.session.get("user_id")
    return Register.objects.filter(id=user_id, status="Active").first() if user_id else None


def is_admin(request):
    return bool(request.session.get("admin"))


def employee_task_queryset(user):
    return Task.objects.filter(
        Q(assigned_employees=user) |
        Q(assigned_employees__isnull=True, assigned_to=user)
    ).distinct()


# ==============================
# LANDING / EMPLOYEE AUTH
# ==============================
def index(request):
    return render(request, "landing/index.html")


def home(request):
    user = current_employee(request)
    if not user:
        return redirect("login")
    return render(request, "landing/home.html", {"user": user})


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

    return render(request, "employee/register.html", {"departments": Department.objects.all()})


def registration_departments(request):
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


def login_view(request):
    return employee_login(request)


def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")
        user = Register.objects.filter(email=email, status="Active").first()
        if not user:
            messages.error(request, "No active employee account was found with that email address.")
        elif not PASSWORD_PATTERN.fullmatch(password):
            messages.error(
                request,
                "Password must be at least 8 characters and include one uppercase letter, one lowercase letter, one number, and one special character.",
            )
        elif password != confirm_password:
            messages.error(request, "Passwords do not match.")
        else:
            user.password = make_password(password)
            user.save(update_fields=["password"])
            messages.success(request, "Password changed successfully. You can now login.")
            return redirect("login")
    return render(request, "employee/forgot_password.html")


def logout(request):
    request.session.flush()
    return redirect("index")


# ==============================
# VISITOR MESSAGES
# ==============================
@csrf_exempt
def visitor_message_submit(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request method."}, status=405)

    name = request.POST.get("name", "").strip()
    email = request.POST.get("email", "").strip().lower()
    message = request.POST.get("message", "").strip()

    if not name or len(name) < 2:
        return JsonResponse({"success": False, "message": "Please enter your name."}, status=400)
    if not email or "@" not in email:
        return JsonResponse({"success": False, "message": "Please enter a valid email address."}, status=400)
    if not message or len(message) < 3:
        return JsonResponse({"success": False, "message": "Please enter a message."}, status=400)

    VisitorMessage.objects.create(name=name, email=email, message=message)
    return JsonResponse({"success": True, "message": "Thanks! Your message has been sent successfully."})


def admin_visitor_messages(request):
    if not request.session.get("admin"):
        return redirect("adminlogin")

    if request.method == "POST":
        action = request.POST.get("action")
        message_id = request.POST.get("message_id")
        if action == "delete" and message_id:
            item = get_object_or_404(VisitorMessage, id=message_id)
            item.delete()
            messages.success(request, "Visitor message deleted.")
        elif action == "clear":
            VisitorMessage.objects.all().delete()
            messages.success(request, "All visitor messages cleared.")
        return redirect("admin_visitor_messages")

    items = VisitorMessage.objects.all()
    items.filter(is_read=False).update(is_read=True)
    return render(request, "admin/visitor_messages.html", {"visitor_messages": items})


# ==============================
# EMPLOYEE DASHBOARD / TASKS
# ==============================
def dashboard(request):
    user = current_employee(request)
    if not user:
        return redirect("login")
    tasks = employee_task_queryset(user)
    task_rows = []
    for task in tasks:
        extension = task.extension_requests.filter(employee=user).first()
        latest_update = task.updates.filter(employee=user).first()
        task_rows.append({
            "task": task,
            "extension_status": extension.status if extension else "Not Requested",
            "latest_progress": latest_update.progress if latest_update else task.progress,
        })
    return render(request, "employee/dashboard.html", {
        "user": user,
        "tasks": tasks,
        "task_rows": task_rows,
        "pending": tasks.filter(status="Pending").count(),
        "progress": tasks.filter(status="In Progress").count(),
        "completed": tasks.filter(status="Completed").count(),
    })


def employee_tasks(request):
    user = current_employee(request)
    if not user:
        return redirect("login")
    return render(request, "employee/tasks.html", {"user": user, "tasks": employee_task_queryset(user)})


def task_detail(request, task_id):
    user = current_employee(request)
    if not user:
        return redirect("login")
    task = get_object_or_404(employee_task_queryset(user), id=task_id)
    return render(request, "employee/task_detail.html", {
        "user": user,
        "task": task,
        "updates": task.updates.filter(employee=user),
        "extensions": task.extension_requests.filter(employee=user),
        "files": task.uploaded_files.filter(employee=user),
    })


def start_task(request, task_id):
    user = current_employee(request)
    if not user:
        return redirect("login")
    task = get_object_or_404(employee_task_queryset(user), id=task_id)
    if request.method == "POST":
        if task.status == "Pending":
            task.status = "In Progress"
            task.save(update_fields=["status"])
            Notification.objects.create(
                recipient=None,
                title="Task started",
                message=f"{user.name} started the task: {task.title}",
            )
            messages.success(request, "Task started. Status changed to In Progress.")
        elif task.status == "In Progress":
            messages.info(request, "This task is already in progress.")
        else:
            messages.info(request, "This task is already completed.")
    return redirect("progress_updates")


def progress_update(request, task_id):
    user = current_employee(request)
    if not user:
        return redirect("login")
    task = get_object_or_404(employee_task_queryset(user), id=task_id)
    if request.method == "POST":
        try:
            progress = max(0, min(100, int(request.POST.get("progress", 0))))
        except (TypeError, ValueError):
            progress = 0
        ProgressUpdate.objects.create(
            task=task,
            employee=user,
            progress=progress,
            note=request.POST.get("note", "").strip(),
        )
        task.progress = progress
        if progress == 100:
            task.status = "Completed"
        elif task.status != "Completed":
            task.status = "In Progress" if progress > 0 or task.status == "In Progress" else "Pending"
        task.save(update_fields=["progress", "status"])
        messages.success(request, "Progress saved successfully.")
    return redirect("progress_updates")


def progress_update_fixed(request, task_id):
    return progress_update(request, task_id)


def progress_edit(request, update_id):
    user = current_employee(request)
    if not user:
        return redirect("login")
    update = get_object_or_404(ProgressUpdate, id=update_id, employee=user)
    if request.method == "POST":
        try:
            update.progress = max(0, min(100, int(request.POST.get("progress", update.progress))))
        except (TypeError, ValueError):
            pass
        update.note = request.POST.get("note", update.note).strip()
        update.save()
        task = update.task
        task.progress = update.progress
        task.status = "Completed" if update.progress == 100 else "In Progress" if update.progress > 0 else task.status
        task.save(update_fields=["progress", "status"])
        messages.success(request, "Progress update edited successfully.")
    return redirect("progress_updates")


def progress_edit_fixed(request, update_id):
    return progress_edit(request, update_id)


def progress_delete(request, update_id):
    user = current_employee(request)
    if not user:
        return redirect("login")
    update = get_object_or_404(ProgressUpdate, id=update_id, employee=user)
    task = update.task
    if request.method == "POST":
        update.delete()
        latest = task.updates.filter(employee=user).first()
        task.progress = latest.progress if latest else 0
        if task.progress == 100:
            task.status = "Completed"
        elif task.progress > 0:
            task.status = "In Progress"
        elif task.status != "Pending":
            task.status = "Pending"
        task.save(update_fields=["progress", "status"])
        messages.success(request, "Progress update deleted.")
    return redirect("progress_updates")


def progress_delete_fixed(request, update_id):
    return progress_delete(request, update_id)


def progress_updates(request):
    user = current_employee(request)
    if not user:
        return redirect("login")
    return render(request, "employee/progress_updates.html", {
        "user": user,
        "tasks": employee_task_queryset(user),
        "updates": user.progress_updates.select_related("task").all(),
    })


def task_file_upload(request, task_id):
    user = current_employee(request)
    if not user:
        return redirect("login")
    task = get_object_or_404(employee_task_queryset(user), id=task_id)
    if request.method == "POST":
        uploaded = request.FILES.get("file")
        if uploaded:
            TaskFile.objects.create(task=task, employee=user, file=uploaded)
            messages.success(request, "Task file uploaded successfully.")
        else:
            messages.error(request, "Please select a file to upload.")
    return redirect("task_detail", task_id=task.id)


def task_file_upload_fixed(request, task_id):
    return task_file_upload(request, task_id)


def task_file_delete(request, file_id):
    user = current_employee(request)
    if not user:
        return redirect("login")
    item = get_object_or_404(TaskFile, id=file_id, employee=user)
    task_id = item.task_id
    if request.method == "POST":
        item.file.delete(save=False)
        item.delete()
        messages.success(request, "Uploaded file deleted.")
    return redirect("task_detail", task_id=task_id)


# ==============================
# EMPLOYEE EXTENSIONS
# ==============================
def request_extension(request, task_id):
    user = current_employee(request)
    if not user:
        return redirect("login")
    task = get_object_or_404(employee_task_queryset(user), id=task_id)
    if request.method == "POST":
        requested_deadline = request.POST.get("requested_deadline")
        reason = request.POST.get("reason", "").strip()
        if requested_deadline and reason:
            ExtensionRequest.objects.create(task=task, employee=user, requested_deadline=requested_deadline, reason=reason)
            messages.success(request, "Extension request submitted successfully.")
        else:
            messages.error(request, "Please provide a new deadline and reason.")
    return redirect("extension_requests_employee")


def extension_requests_employee(request):
    user = current_employee(request)
    if not user:
        return redirect("login")
    return render(request, "employee/extension_requests.html", {
        "user": user,
        "tasks": employee_task_queryset(user),
        "requests": user.extension_requests.select_related("task").all(),
    })


def extension_edit(request, request_id):
    user = current_employee(request)
    if not user:
        return redirect("login")
    extension = get_object_or_404(ExtensionRequest, id=request_id, employee=user)
    if request.method == "POST" and extension.status == "Pending":
        extension.requested_deadline = request.POST.get("requested_deadline", extension.requested_deadline)
        extension.reason = request.POST.get("reason", extension.reason).strip()
        extension.save()
        messages.success(request, "Extension request edited successfully.")
    return redirect("extension_requests_employee")


def extension_delete(request, request_id):
    user = current_employee(request)
    if not user:
        return redirect("login")
    extension = get_object_or_404(ExtensionRequest, id=request_id, employee=user)
    if request.method == "POST" and extension.status == "Pending":
        extension.delete()
        messages.success(request, "Extension request deleted.")
    return redirect("extension_requests_employee")


# ==============================
# EMPLOYEE NOTIFICATIONS / MESSAGES
# ==============================
def notifications(request):
    user = current_employee(request)
    if not user:
        return redirect("login")
    items = Notification.objects.filter(recipient=user).order_by("-created_at")
    items.filter(is_read=False).update(is_read=True)
    return render(request, "employee/notifications.html", {"user": user, "notifications": items})


def clear_notifications(request):
    user = current_employee(request)
    if not user:
        return redirect("login")
    if request.method == "POST":
        Notification.objects.filter(recipient=user).delete()
        messages.success(request, "Notifications cleared.")
    return redirect("notifications")


def messages_view_fixed(request):
    user = current_employee(request)
    if not user:
        return redirect("login")
    if request.method == "POST":
        recipient_id = request.POST.get("recipient")
        subject = request.POST.get("subject", "").strip()
        body = request.POST.get("body", "").strip()
        if recipient_id == "admin":
            Message.objects.create(sender=user, recipient=None, subject=subject, body=body, is_admin_recipient=True)
            messages.success(request, "Message sent to administrator.")
        elif recipient_id and subject and body:
            recipient = get_object_or_404(Register, id=recipient_id, status="Active")
            Message.objects.create(sender=user, recipient=recipient, subject=subject, body=body)
            messages.success(request, "Message sent successfully.")
    received = Message.objects.filter(Q(sender=user) | Q(recipient=user)).select_related("sender", "recipient")
    Message.objects.filter(recipient=user, is_read=False).update(is_read=True)
    employees = Register.objects.filter(status="Active").exclude(id=user.id).order_by("name")
    return render(request, "employee/messages.html", {"user": user, "received": received, "employees": employees})


def messages_view(request):
    return messages_view_fixed(request)


def clear_messages(request):
    user = current_employee(request)
    if not user:
        return redirect("login")
    if request.method == "POST":
        Message.objects.filter(Q(sender=user) | Q(recipient=user)).delete()
        messages.success(request, "Messages cleared.")
    return redirect("messages")


# ==============================
# ADMIN AUTH / MANAGEMENT
# ==============================
def adminlogin(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        if ADMIN_EMAIL and ADMIN_PASSWORD and email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            request.session["admin"] = email
            return redirect("admin_dash")
        messages.error(request, "Invalid admin login or administrator credentials are not configured.")
    return render(request, "admin/adminlogin.html")


def admin_dash(request):
    if not is_admin(request):
        return redirect("adminlogin")
    return render(request, "admin/dashboard.html", {
        "total_employees": Register.objects.count(),
        "active_employees": Register.objects.filter(status="Active").count(),
        "total_tasks": Task.objects.count(),
        "pending_tasks": Task.objects.filter(status="Pending").count(),
        "progress_tasks": Task.objects.filter(status="In Progress").count(),
        "pending_extensions": ExtensionRequest.objects.filter(status="Pending").count(),
        "completed_tasks": Task.objects.filter(status="Completed").count(),
        "employees": Register.objects.select_related("department").order_by("name")[:8],
    })


def adminlogout(request):
    request.session.flush()
    return redirect("index")


def employee_management(request):
    if not is_admin(request):
        return redirect("adminlogin")
    return render(request, "admin/employees.html", {"employees": Register.objects.select_related("department").order_by("name"), "departments": Department.objects.all()})


def employee_edit(request, employee_id):
    if not is_admin(request):
        return redirect("adminlogin")
    employee = get_object_or_404(Register, id=employee_id)
    if request.method == "POST":
        employee.name = request.POST.get("name", employee.name).strip()
        employee.phone = request.POST.get("phone", employee.phone).strip()
        employee.status = request.POST.get("status", employee.status)
        department_id = request.POST.get("department") or None
        employee.department_id = department_id
        employee.designation = request.POST.get("designation", employee.designation).strip()
        employee.save()
        if department_id:
            EmployeeDepartment.objects.update_or_create(employee=employee, defaults={"department_id": department_id})
        else:
            EmployeeDepartment.objects.filter(employee=employee).update(department=None)
        messages.success(request, "Employee updated.")
        return redirect("employee_management")
    return render(request, "admin/employee_form.html", {"employee": employee, "departments": Department.objects.all(), "assignment": getattr(employee, "department_assignment", None)})


def employee_delete(request, employee_id):
    if not is_admin(request):
        return redirect("adminlogin")
    if request.method == "POST":
        employee = get_object_or_404(Register, id=employee_id)
        name = employee.name
        employee.delete()
        messages.success(request, f"Employee {name} deleted successfully.")
    return redirect("employee_management")


def department_management(request):
    if not is_admin(request):
        return redirect("adminlogin")
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()
        if name:
            Department.objects.get_or_create(name=name, defaults={"description": description})
        return redirect("department_management")
    return render(request, "admin/departments.html", {"departments": Department.objects.annotate(employee_count=Count("employees"))})


def department_delete(request, department_id):
    if not is_admin(request):
        return redirect("adminlogin")
    if request.method == "POST":
        get_object_or_404(Department, id=department_id).delete()
    return redirect("department_management")


def task_management(request):
    if not is_admin(request):
        return redirect("adminlogin")
    return render(request, "admin/tasks.html", {"tasks": Task.objects.select_related("assigned_to", "department").prefetch_related("assigned_employees", "uploaded_files__employee"), "employees": Register.objects.filter(status="Active"), "departments": Department.objects.all()})


def assign_task(request):
    if not is_admin(request):
        return redirect("adminlogin")
    if request.method == "POST":
        employee_ids = request.POST.getlist("assigned_to")
        employees = list(Register.objects.filter(id__in=employee_ids, status="Active"))
        if not employees:
            messages.error(request, "Please select at least one employee.")
            return redirect("task_management")
        task = Task.objects.create(title=request.POST.get("title", "").strip(), description=request.POST.get("description", "").strip(), assigned_to=employees[0], department_id=request.POST.get("department") or None, deadline=request.POST.get("deadline"), priority=request.POST.get("priority", "Medium"))
        task.assigned_employees.set(employees)
        for employee in employees:
            Notification.objects.create(recipient=employee, title="New task assigned", message=f"You have been assigned: {task.title}")
            if employee.email:
                try:
                    send_mail("WorkSphere - New Task Assigned", f"Hello {employee.name},\n\nA new task has been assigned to you.\n\nTask: {task.title}\nDescription: {task.description}\nPriority: {task.priority}\nDeadline: {task.deadline}", None, [employee.email], fail_silently=True)
                except Exception:
                    pass
        messages.success(request, f"Task assigned to {len(employees)} employee(s).")
    return redirect("task_management")


def task_edit(request, task_id):
    if not is_admin(request):
        return redirect("adminlogin")
    task = get_object_or_404(Task, id=task_id)
    if request.method == "POST":
        employee_ids = request.POST.getlist("assigned_to")
        employees = list(Register.objects.filter(id__in=employee_ids, status="Active"))
        if not employees:
            messages.error(request, "Please select at least one employee.")
            return redirect("task_edit", task_id=task.id)
        task.title = request.POST.get("title", task.title).strip()
        task.description = request.POST.get("description", task.description).strip()
        task.department_id = request.POST.get("department") or None
        task.deadline = request.POST.get("deadline", task.deadline)
        task.priority = request.POST.get("priority", task.priority)
        task.assigned_to = employees[0]
        task.save()
        task.assigned_employees.set(employees)
        messages.success(request, "Task updated successfully.")
        return redirect("task_management")
    return render(request, "admin/task_form.html", {"task": task, "employees": Register.objects.filter(status="Active"), "departments": Department.objects.all(), "selected_employees": task.assigned_employees.all()})


def task_delete(request, task_id):
    if not is_admin(request):
        return redirect("adminlogin")
    if request.method == "POST":
        task = get_object_or_404(Task, id=task_id)
        title = task.title
        task.delete()
        messages.success(request, f"Task {title} deleted successfully.")
    return redirect("task_management")


def admin_task_files(request):
    if not is_admin(request):
        return redirect("adminlogin")
    return render(request, "admin/task_files.html", {"files": TaskFile.objects.select_related("task", "employee").all()})


def admin_task_file_delete(request, file_id):
    if not is_admin(request):
        return redirect("adminlogin")
    item = get_object_or_404(TaskFile, id=file_id)
    if request.method == "POST":
        item.file.delete(save=False)
        item.delete()
        messages.success(request, "Task file deleted.")
    return redirect("admin_task_files")


def extension_requests(request):
    if not is_admin(request):
        return redirect("adminlogin")
    return render(request, "admin/extensions.html", {"requests": ExtensionRequest.objects.select_related("task", "employee").all()})


def extension_action(request, request_id, action):
    if not is_admin(request):
        return redirect("adminlogin")
    extension = get_object_or_404(ExtensionRequest, id=request_id)
    if request.method == "POST" and action in ("approve", "reject"):
        extension.status = "Approved" if action == "approve" else "Rejected"
        extension.admin_note = request.POST.get("admin_note", "").strip()
        extension.save()
        if extension.status == "Approved":
            extension.task.deadline = extension.requested_deadline
            extension.task.save(update_fields=["deadline"])
        Notification.objects.create(recipient=extension.employee, title=f"Extension {extension.status}", message=f"Your extension request for {extension.task.title} was {extension.status.lower()}.")
    return redirect("extension_requests")


def reports(request):
    if not is_admin(request):
        return redirect("adminlogin")
    tasks = Task.objects.all()
    by_department = Department.objects.annotate(task_count=Count("tasks")).order_by("name")
    return render(request, "admin/reports.html", {"total": tasks.count(), "pending": tasks.filter(status="Pending").count(), "progress": tasks.filter(status="In Progress").count(), "completed": tasks.filter(status="Completed").count(), "by_department": by_department})


def admin_notifications(request):
    if not is_admin(request):
        return redirect("adminlogin")
    items = Notification.objects.filter(recipient__isnull=True).order_by("-created_at")
    items.filter(is_read=False).update(is_read=True)
    return render(request, "admin/notifications.html", {"notifications": items})


def admin_clear_notifications(request):
    if not is_admin(request):
        return redirect("adminlogin")
    if request.method == "POST":
        Notification.objects.filter(recipient__isnull=True).delete()
        messages.success(request, "Administrator notifications cleared.")
    return redirect("admin_notifications")


def admin_messages(request):
    if not is_admin(request):
        return redirect("adminlogin")
    if request.method == "POST":
        recipient_id = request.POST.get("recipient")
        recipient = get_object_or_404(Register, id=recipient_id, status="Active")
        Message.objects.create(sender=None, recipient=recipient, subject=request.POST.get("subject", "").strip(), body=request.POST.get("body", "").strip(), is_admin_sender=True)
        Notification.objects.create(recipient=recipient, title="New message from administrator", message="You have received a new message from the administrator.")
        messages.success(request, "Message sent successfully.")
    messages_list = Message.objects.filter(Q(is_admin_sender=True) | Q(is_admin_recipient=True)).select_related("sender", "recipient")
    Message.objects.filter(is_admin_recipient=True, is_read=False).update(is_read=True)
    return render(request, "admin/messages.html", {"messages_list": messages_list, "employees": Register.objects.filter(status="Active").order_by("name")})


def admin_clear_messages(request):
    if not is_admin(request):
        return redirect("adminlogin")
    if request.method == "POST":
        Message.objects.filter(Q(is_admin_sender=True) | Q(is_admin_recipient=True)).delete()
        messages.success(request, "Administrator messages cleared.")
    return redirect("admin_messages")


def admin_message_reply(request, message_id):
    if not is_admin(request):
        return redirect("adminlogin")
    original = get_object_or_404(Message, id=message_id, is_admin_recipient=True)
    if request.method == "POST" and original.sender:
        subject = request.POST.get("subject", f"Re: {original.subject}").strip()
        body = request.POST.get("body", "").strip()
        Message.objects.create(sender=None, recipient=original.sender, subject=subject, body=body, is_admin_sender=True)
        Notification.objects.create(recipient=original.sender, title="Admin replied to your message", message=f"The administrator replied to your message: {original.subject}")
        messages.success(request, f"Reply sent to {original.sender.name}.")
    return redirect("admin_messages")


def profile(request):
    user = current_employee(request)
    if not user:
        return redirect("login")
    return render(request, "employee/profile.html", {"user": user})


def settings_view(request):
    user = current_employee(request)
    if not user:
        return redirect("login")
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "account":
            name = request.POST.get("name", "").strip()
            phone = request.POST.get("phone", "").strip()
            photo = request.FILES.get("profile_photo")
            if len(name) < 3 or not phone.isdigit() or len(phone) != 10:
                messages.error(request, "Please enter a valid name and 10-digit phone number.")
            else:
                user.name = name
                user.phone = phone
                if photo:
                    user.profile_photo = photo
                user.save()
                messages.success(request, "Account settings saved.")
        elif action == "password":
            current = request.POST.get("current_password", "")
            new_password = request.POST.get("new_password", "")
            confirm = request.POST.get("confirm_password", "")
            if not check_password(current, user.password):
                messages.error(request, "Current password is incorrect.")
            elif not PASSWORD_PATTERN.fullmatch(new_password):
                messages.error(request, "New password must contain uppercase, lowercase, number, special character and at least 8 characters.")
            elif new_password != confirm:
                messages.error(request, "New passwords do not match.")
            else:
                user.password = make_password(new_password)
                user.save(update_fields=["password"])
                messages.success(request, "Password changed successfully.")
    return render(request, "employee/settings.html", {"user": user})


def admin_profile(request):
    if not is_admin(request):
        return redirect("adminlogin")
    return render(request, "admin/profile.html", {"admin_email": request.session.get("admin", ADMIN_EMAIL)})


def notification_badges(request):
    employee = current_employee(request)
    employee_notification_count = employee.notifications.filter(is_read=False).count() if employee else 0
    employee_message_count = Message.objects.filter(recipient=employee, is_read=False).count() if employee else 0
    if not is_admin(request):
        return {"admin_notification_count": 0, "admin_message_count": 0, "admin_extension_count": 0, "employee_notification_count": employee_notification_count, "employee_message_count": employee_message_count}
    return {"admin_notification_count": Notification.objects.filter(recipient__isnull=True, is_read=False).count(), "admin_message_count": Message.objects.filter(is_admin_recipient=True, is_read=False).count(), "admin_extension_count": ExtensionRequest.objects.filter(status="Pending").count(), "employee_notification_count": employee_notification_count, "employee_message_count": employee_message_count}


@receiver(post_save, sender=Message, dispatch_uid="worksphere_admin_message_notification")
def notify_admin_about_employee_message(sender, instance, created, **kwargs):
    if created and instance.is_admin_recipient and instance.sender_id:
        Notification.objects.create(recipient=None, title="New employee message", message=f"{instance.sender.name} sent a message to the administrator.")


@receiver(post_save, sender=ExtensionRequest, dispatch_uid="worksphere_admin_extension_notification")
def notify_admin_about_extension_request(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(recipient=None, title="New extension request", message=f"{instance.employee.name} requested an extension for {instance.task.title}.")


@receiver(post_save, sender=ProgressUpdate, dispatch_uid="worksphere_admin_progress_notification")
def notify_admin_about_progress_update(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(recipient=None, title="Employee progress updated", message=f"{instance.employee.name} updated progress for {instance.task.title} to {instance.progress}%.")


@receiver(post_save, sender=TaskFile, dispatch_uid="worksphere_admin_file_notification")
def notify_admin_about_employee_file(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(recipient=None, title="New employee file uploaded", message=f"{instance.employee.name} uploaded a file for {instance.task.title}.")
