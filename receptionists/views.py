from django.shortcuts import render


def schedule_management_view(request):
    return render(
        request,
        "receptionists/schedule_management.html",
        {
            "current_role": "Receptionist",
        },
    )


def checkin_view(request):
    return render(
        request,
        "receptionists/checkin.html",
        {
            "current_role": "Receptionist",
        },
    )
