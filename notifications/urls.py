from django.urls import path
from .views import (
    NotificationListView,
    MarkNotificationAsReadView,
    MarkAllNotificationsAsReadView,
)

app_name = "notifications"

urlpatterns = [
    path("", NotificationListView.as_view(), name="list"),
    path("read/", MarkNotificationAsReadView.as_view(), name="mark_as_read"),
    path("read-all/", MarkAllNotificationsAsReadView.as_view(), name="mark_all_as_read"),
]