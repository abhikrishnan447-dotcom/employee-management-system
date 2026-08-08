from pathlib import Path
import zipfile

from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect

from .models import Message, Notification, ProgressUpdate, TaskFile
from .views import ADMIN_EMAIL, current_employee, employee_task_queryset


def _task_employee_progress(task, employee):
    latest = task.updates.filter(employee=employee).order_by("-created_at").first()
    return latest.progress if latest else 0


def _refresh_task_progress(task):
    employees = list(task.assigned_employees.all())
    if not employees and task.assigned_to_id:
        employees = [task.assigned_to]

    values = [_task_employee_progress(task, employee) for employee in employees]
    task.progress = round(sum(values) / len(values)) if values else 0
    task.status = (
        "Completed" if values and all(value == 100 for value in values)
        else "In Progress" if any(value > 0 for value in values)
        else "Pending"
    )
    task.save(update_fields=["progress", "status"])
    return task.progress, task.status


def progress_update_fixed(request, task_id):
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
        task.refresh_from_db()
        _, status = _refresh_task_progress(task)

        if status == "Completed":
            subject = f"Task completed: {task.title}"
            body = f"All assigned employees have completed the task '{task.title}'."
            Message.objects.create(
                sender=user,
                recipient=None,
                subject=subject,
                body=body,
                is_admin_recipient=True,
                is_read=False,
            )
            if ADMIN_EMAIL:
                try:
                    send_mail(
                        f"WorkSphere - {subject}",
                        body,
                        None,
                        [ADMIN_EMAIL],
                        fail_silently=False,
                    )
                except Exception:
                    pass
            messages.success(request, "Task completed. The administrator has been notified.")
        else:
            messages.success(request, "Progress updated successfully.")

    return redirect("progress_updates")


def progress_edit_fixed(request, update_id):
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
        _refresh_task_progress(update.task)
        messages.success(request, "Progress update edited successfully.")

    return redirect("progress_updates")


def progress_delete_fixed(request, update_id):
    user = current_employee(request)
    if not user:
        return redirect("login")
    update = get_object_or_404(ProgressUpdate, id=update_id, employee=user)
    task = update.task

    if request.method == "POST":
        update.delete()
        _refresh_task_progress(task)
        messages.success(request, "Progress update deleted.")

    return redirect("progress_updates")


def task_file_upload_fixed(request, task_id):
    user = current_employee(request)
    if not user:
        return redirect("login")
    task = get_object_or_404(employee_task_queryset(user), id=task_id)

    if request.method == "POST":
        uploaded = request.FILES.get("file")
        if not uploaded:
            messages.error(request, "Please select a ZIP file to upload.")
            return redirect("task_detail", task_id=task.id)

        if Path(uploaded.name).suffix.lower() != ".zip":
            messages.error(request, "Only ZIP files are allowed.")
            return redirect("task_detail", task_id=task.id)

        try:
            if not zipfile.is_zipfile(uploaded):
                messages.error(request, "The selected file is not a valid ZIP archive.")
                return redirect("task_detail", task_id=task.id)
            uploaded.seek(0)
        except (OSError, ValueError):
            messages.error(request, "Unable to validate the ZIP file.")
            return redirect("task_detail", task_id=task.id)

        TaskFile.objects.create(task=task, employee=user, file=uploaded)
        messages.success(request, "ZIP file uploaded successfully.")

    return redirect("task_detail", task_id=task.id)
