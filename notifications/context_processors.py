from notifications.models import Notification


def notifications_nav(request):
    if not request.user.is_authenticated:
        return {
            "nav_notifications": [],
            "nav_notifications_unread_count": 0,
        }

    notifications = Notification.objects.filter(user=request.user)

    return {
        "nav_notifications": notifications[:5],
        "nav_notifications_unread_count": notifications.filter(is_read=False).count(),
    }
