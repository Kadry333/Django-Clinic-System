from django.contrib.auth import get_user_model

from notifications.models import Notification


def get_receptionist_users():
    User = get_user_model()
    return User.objects.filter(
        groups__name="receptionist",
        is_active=True,
    ).distinct()


def notify_receptionists(title, message, notification_type):
    receptionists = get_receptionist_users()

    Notification.objects.bulk_create(
        [
            Notification(
                user=receptionist,
                title=title,
                message=message,
                notification_type=notification_type,
            )
            for receptionist in receptionists
        ]
    )


def create_notification(user, title, message, notification_type):
    if not user:
        return None

    return Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type,
    )