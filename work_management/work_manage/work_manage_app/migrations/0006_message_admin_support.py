from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("work_manage_app", "0005_task_assigned_employees")]

    operations = [
        migrations.AlterField(
            model_name="message",
            name="sender",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="sent_messages", to="work_manage_app.register"),
        ),
        migrations.AlterField(
            model_name="message",
            name="recipient",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="received_messages", to="work_manage_app.register"),
        ),
        migrations.AddField(
            model_name="message",
            name="is_admin_sender",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="message",
            name="is_admin_recipient",
            field=models.BooleanField(default=False),
        ),
    ]
