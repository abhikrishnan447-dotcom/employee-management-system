from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("work_manage_app", "0009_move_designation_to_register"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notification",
            name="recipient",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.deletion.CASCADE,
                related_name="notifications",
                to="work_manage_app.register",
            ),
        ),
    ]
