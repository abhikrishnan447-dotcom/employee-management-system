from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("work_manage_app", "0008_sync_employee_departments"),
    ]

    operations = [
        migrations.AddField(
            model_name="notification",
            name="employee_cleared",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="notification",
            name="admin_cleared",
            field=models.BooleanField(default=False),
        ),
    ]
