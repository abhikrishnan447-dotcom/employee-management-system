from django.db import migrations, models
import django.db.models.deletion


def copy_existing_assignments(apps, schema_editor):
    Task = apps.get_model("work_manage_app", "Task")
    for task in Task.objects.all():
        if task.assigned_to_id:
            task.assigned_employees.add(task.assigned_to_id)


class Migration(migrations.Migration):
    dependencies = [("work_manage_app", "0004_work_management_features")]

    operations = [
        migrations.AddField(
            model_name="task",
            name="assigned_employees",
            field=models.ManyToManyField(blank=True, related_name="assigned_tasks", to="work_manage_app.register"),
        ),
        migrations.RunPython(copy_existing_assignments, migrations.RunPython.noop),
    ]
