from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import ListView, View

from notifications.models import Notification
from notifications.forms import MarkNotificationAsReadForm


class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = "notifications/list.html"
    context_object_name = "notifications"

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


class MarkNotificationAsReadView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        form = MarkNotificationAsReadForm(request.POST)

        if form.is_valid():
            notification = get_object_or_404(
                Notification,
                id=form.cleaned_data["notification_id"],
                user=request.user
            )
            notification.is_read = True
            notification.save()

        return redirect("notifications:list")


class MarkAllNotificationsAsReadView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True)

        return redirect("notifications:list")