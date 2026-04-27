from datetime import datetime, timedelta

from django.utils import timezone

from appointments.models import Appointment
from doctors.models import DoctorSchedule, DoctorScheduleException


WEEKDAY_TO_SCHEDULE_DAY = {
    0: "mon",
    1: "tue",
    2: "wed",
    3: "thu",
    4: "fri",
    5: "sat",
    6: "sun",
}

UNAVAILABLE_APPOINTMENT_STATUSES = [
    "requested",
    "confirmed",
    "checked_in",
    "completed",
]


def _generate_window_slots(start_time, end_time, session_duration, buffer_time):
    increment_minutes = session_duration + buffer_time
    current = datetime.combine(datetime.today(), start_time)
    boundary = datetime.combine(datetime.today(), end_time)

    while current + timedelta(minutes=session_duration) <= boundary:
        yield current.time()
        current += timedelta(minutes=increment_minutes)


def get_available_slots(doctor, appointment_date, exclude_appointment=None):
    if not doctor or not appointment_date:
        return []

    if appointment_date < timezone.localdate():
        return []

    exception = (
        DoctorScheduleException.objects.filter(doctor=doctor, date=appointment_date)
        .order_by("-id")
        .first()
    )

    if exception:
        if exception.is_day_off:
            return []

        if not exception.start_time or not exception.end_time:
            return []

        working_windows = [(exception.start_time, exception.end_time)]
    else:
        weekday_code = WEEKDAY_TO_SCHEDULE_DAY[appointment_date.weekday()]

        working_windows = list(
            DoctorSchedule.objects.filter(
                doctor=doctor, day_of_week=weekday_code
            ).values_list("start_time", "end_time")
        )

        if not working_windows:
            return []

    booked_appointments = Appointment.objects.filter(
        doctor=doctor,
        appointment_date=appointment_date,
        status__in=UNAVAILABLE_APPOINTMENT_STATUSES,
    )
    if exclude_appointment is not None:
        booked_appointments = booked_appointments.exclude(pk=exclude_appointment.pk)

    booked_slots = set(booked_appointments.values_list("start_time", flat=True))

    available_slots = []

    for start_time, end_time in working_windows:
        for slot in _generate_window_slots(
            start_time=start_time,
            end_time=end_time,
            session_duration=doctor.session_duration,
            buffer_time=doctor.buffer_time,
        ):
            if slot not in booked_slots:
                available_slots.append(slot)

    return sorted(set(available_slots))
