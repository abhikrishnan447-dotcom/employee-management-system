from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Count
from django.core.mail import send_mail
from .models import Register, Department, EmployeeDepartment, Task, ExtensionRequest, ProgressUpdate, Notification
import os

# ... existing functions above remain unchanged ...

def employee_edit(request, employee_id):
    if not is_admin(request): return redirect("adminlogin")
    employee = get_object_or_404(Register, id=employee_id)
    if request.method == "POST":
        employee.name = request.POST.get("name", employee.name).strip()
        # Registered email is intentionally immutable after registration.
        employee.phone = request.POST.get("phone", employee.phone).strip()
        employee.status = request.POST.get("status", employee.status)
        department_id = request.POST.get("department") or None
        employee.department_id = department_id
        employee.save()
        EmployeeDepartment.objects.update_or_create(employee=employee, defaults={"department_id": department_id, "designation": request.POST.get("designation", "")})
        messages.success(request, "Employee updated.")
        return redirect("employee_management")
    return render(request, "admin/employee_form.html", {"employee": employee, "departments": Department.objects.all(), "assignment": getattr(employee, "department_assignment", None)})
