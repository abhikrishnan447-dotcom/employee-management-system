from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("work_manage_app", "0010_allow_admin_notifications"),
    ]

    operations = [
        migrations.CreateModel(
            name="VisitorMessage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("email", models.EmailField(max_length=254)),
                ("message", models.TextField()),
                ("is_read", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
