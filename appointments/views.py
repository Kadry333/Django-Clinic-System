from django.shortcuts import render


def patient_book_view(request):
    return render(
        request,
        "appointments/book.html",
        {
            "current_role": "Patient",
        },
    )


def patient_appointments_view(request):
    return render(
        request,
        "appointments/my_appointments.html",
        {
            "current_role": "Patient",
        },
    )


def doctor_management_view(request):
    return render(
        request,
        "appointments/doctor_management.html",
        {
            "current_role": "Doctor",
        },
    )


def receptionist_bookings_view(request):
    return render(
        request,
        "appointments/receptionist_bookings.html",
        {
            "current_role": "Receptionist",
        },
    )


def receptionist_reschedule_view(request):
    return render(
        request,
        "appointments/receptionist_reschedule.html",
        {
            "current_role": "Receptionist",
        },
    )
