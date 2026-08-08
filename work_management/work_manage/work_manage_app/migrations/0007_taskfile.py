from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("work_manage_app", "0006_message_admin_support")]

    operations = [
        migrations.CreateModel(
            name="TaskFile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("file", models.FileField(upload_to="task_files/")),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                ("employee", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="task_files", to="work_manage_app.register")),
                ("task", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="uploaded_files", to="work_manage_app.task")),
            ],
            options={"ordering": ["-uploaded_at"]},
        ),
    ]
