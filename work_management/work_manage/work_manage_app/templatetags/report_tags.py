from django import template
from django.db.models import Sum
from ..models import Task, TaskFile

register = template.Library()


@register.simple_tag
def report_tasks():
    """Return report data grouped by task with per-employee progress."""
    rows = []
    tasks = Task.objects.select_related("assigned_to", "department").prefetch_related(
        "assigned_employees", "updates__employee"
    )

    for task in tasks:
        employees = list(task.assigned_employees.all())
        if not employees and task.assigned_to_id:
            employees = [task.assigned_to]
        if not employees:
            continue

        employee_rows = []
        percentages = []
        for employee in employees:
            rejected_ids = TaskFile.objects.filter(task=task, employee=employee, review_status="Rejected", progress_update__isnull=False).values_list("progress_update_id", flat=True)
            percentage = task.updates.filter(employee=employee).exclude(id__in=rejected_ids).aggregate(total=Sum("progress"))["total"] or 0
            percentage = max(0, min(100, int(percentage)))
            percentages.append(percentage)
            employee_rows.append({
                "employee": employee,
                "percentage": percentage,
                "completed": percentage == 100,
            })

        overall = round(sum(percentages) / len(percentages)) if percentages else 0
        rows.append({
            "task": task,
            "employee_rows": employee_rows,
            "employee_count": len(employee_rows),
            "is_multiple": len(employee_rows) > 1,
            "overall": overall,
            "completed": overall == 100,
        })

    return rows
