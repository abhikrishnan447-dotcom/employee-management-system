from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect

from .models import Notification, Task


def start_task(request, task_id):
    """Mark an assigned task as started without changing its progress percentage."""
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    task = get_object_or_404(
        Task.objects.filter(assigned_employees__id=user_id).distinct(),
        id=task_id,
    )

    if request.method == "POST":
        if task.status == "Pending":
            task.status = "In Progress"
            task.save(update_fields=["status"])
            employee = task.assigned_employees.filter(id=user_id).first()
            if employee:
                Notification.objects.create(
                    recipient=None,
                    title="Task started",
                    message=f"{employee.name} started the task: {task.title}",
                )
            messages.success(request, "Task started. Status changed to In Progress.")
        elif task.status == "In Progress":
            messages.info(request, "This task is already in progress.")
        elif task.status == "Completed":
            messages.info(request, "This task is already completed.")

    return redirect("progress_updates")
