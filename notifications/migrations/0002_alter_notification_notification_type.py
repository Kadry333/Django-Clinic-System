from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notifications", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notification",
            name="notification_type",
            field=models.CharField(
                choices=[
                    ("confirmed", "Confirmed"),
                    ("cancelled", "Cancelled"),
                    ("rescheduled", "Rescheduled"),
                    ("appointment_requested", "Appointment Requested"),
                    ("profile_updated", "Profile Updated"),
                ],
                max_length=40,
            ),
        ),
    ]
