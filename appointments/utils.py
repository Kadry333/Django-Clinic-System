from datetime import datetime, timedelta
from django.utils import timezone

from appointments.models import Appointment
from doctors.models import DoctorSchedule, DoctorScheduleException


def generate_slots(doctor, date):
    now = timezone.localtime()

    if date < now.date():
        return []

    day = date.strftime('%a').lower()[:3]

    exception = DoctorScheduleException.objects.filter(
        doctor=doctor,
        date=date
    ).first()

    if exception:
        if exception.is_day_off:
            return []
        start = exception.start_time
        end = exception.end_time
    else:
        schedule = DoctorSchedule.objects.filter(
            doctor=doctor,
            day_of_week=day
        ).first()

        if not schedule:
            return []

        start = schedule.start_time
        end = schedule.end_time

    booked = Appointment.objects.filter(
        doctor=doctor,
        appointment_date=date
    ).values_list('start_time', flat=True)

    slots = []
    current = timezone.make_aware(datetime.combine(date, start))
    end_dt = timezone.make_aware(datetime.combine(date, end))

    duration = doctor.session_duration
    buffer = doctor.buffer_time

    while current + timedelta(minutes=duration) <= end_dt:
        slot_time = current.time()

        if date == now.date() and current <= now:
            current += timedelta(minutes=duration + buffer)
            continue

        if slot_time not in booked:
            slots.append(current.strftime("%I:%M %p"))

        current += timedelta(minutes=duration + buffer)

    return slots