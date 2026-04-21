from django.shortcuts import render


def summary_view(request):
    return render(
        request,
        "consultations/summary.html",
        {
            "current_role": "Patient",
        },
    )


def doctor_consultation_view(request):
    return render(
        request,
        "consultations/doctor_consultation.html",
        {
            "current_role": "Doctor",
        },
    )
