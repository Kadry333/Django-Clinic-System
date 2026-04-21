from django.shortcuts import render


def dashboard_view(request):
    return render(
        request,
        "doctors/dashboard.html",
        {
            "current_role": "Doctor",
        },
    )


def schedule_view(request):
    return render(
        request,
        "doctors/schedule.html",
        {
            "current_role": "Doctor",
        },
    )
