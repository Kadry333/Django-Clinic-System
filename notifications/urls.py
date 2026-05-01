from django.urls import path
from .views import (
    NotificationListView,
    MarkNotificationAsReadView,
    MarkAllNotificationsAsReadView,
)

app_name = "notifications"

urlpatterns = [
    path("", NotificationListView.as_view(), name="list"),
    path("read/", MarkNotificationAsReadView.as_view(), name="mark.as.read"),
    path("read-all/", MarkAllNotificationsAsReadView.as_view(), name="mark.all.as.read"),
]
