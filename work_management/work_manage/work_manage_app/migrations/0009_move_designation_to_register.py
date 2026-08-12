from django.db import migrations, models


def copy_designations(apps, schema_editor):
    Register = apps.get_model("work_manage_app", "Register")
    EmployeeDepartment = apps.get_model("work_manage_app", "EmployeeDepartment")

    for assignment in EmployeeDepartment.objects.select_related("employee").all().iterator():
        if assignment.designation:
            Register.objects.filter(pk=assignment.employee_id).update(
                designation=assignment.designation
            )


def reverse_copy_designations(apps, schema_editor):
    Register = apps.get_model("work_manage_app", "Register")
    EmployeeDepartment = apps.get_model("work_manage_app", "EmployeeDepartment")

    for employee in Register.objects.all().iterator():
        assignment = EmployeeDepartment.objects.filter(employee_id=employee.id).first()
        if assignment:
            assignment.designation = employee.designation
            assignment.save(update_fields=["designation"])


class Migration(migrations.Migration):
    dependencies = [("work_manage_app", "0008_sync_employee_departments")]

    operations = [
        migrations.AddField(
            model_name="register",
            name="designation",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.RunPython(copy_designations, reverse_copy_designations),
        migrations.RemoveField(
            model_name="employeedepartment",
            name="designation",
        ),
    ]
