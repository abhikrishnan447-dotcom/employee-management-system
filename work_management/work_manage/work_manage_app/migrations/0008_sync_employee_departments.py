from django.db import migrations, models
import django.db.models.deletion


def sync_employee_departments(apps, schema_editor):
    Register = apps.get_model("work_manage_app", "Register")
    EmployeeDepartment = apps.get_model("work_manage_app", "EmployeeDepartment")

    for employee in Register.objects.all().iterator():
        assignment, _ = EmployeeDepartment.objects.get_or_create(employee_id=employee.id)
        assignment.department_id = employee.department_id
        assignment.save(update_fields=["department"])


def reverse_sync(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [("work_manage_app", "0007_taskfile")]

    operations = [
        migrations.AddField(
            model_name="register",
            name="department",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="registered_employees",
                to="work_manage_app.department",
            ),
        ),
        migrations.RunPython(sync_employee_departments, reverse_sync),
    ]
