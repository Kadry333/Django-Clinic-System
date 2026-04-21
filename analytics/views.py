from django.shortcuts import render


def admin_dashboard_view(request):
    return render(
        request,
        "analytics/admin_dashboard.html",
        {
            "current_role": "Admin",
        },
    )


def dashboard_view(request):
    return render(
        request,
        "analytics/dashboard.html",
        {
            "current_role": "Admin",
        },
    )
