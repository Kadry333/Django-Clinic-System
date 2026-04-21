from django.shortcuts import render


def profile_view(request):
    return render(
        request,
        "patients/profile.html",
        {
            "current_role": "Patient",
        },
    )
