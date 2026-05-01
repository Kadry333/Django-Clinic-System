from django import forms


class MarkNotificationAsReadForm(forms.Form):
    notification_id = forms.IntegerField(widget=forms.HiddenInput())


class ClearNotificationForm(forms.Form):
    notification_id = forms.IntegerField(widget=forms.HiddenInput())
