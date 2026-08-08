from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect

from .models import Register
from .views import is_admin


def employee_delete(request, employee_id):
    if not is_admin(request):
        return redirect("adminlogin")
    if request.method != "POST":
        return redirect("admin_dash")

    employee = get_object_or_404(Register, id=employee_id)
    employee_name = employee.name
    employee.delete()
    messages.success(request, f"Employee {employee_name} was deleted successfully.")
    return redirect("admin_dash")
