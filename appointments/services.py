from datetime import datetime, timedelta
from django.db import transaction
from django.utils import timezone
from doctors.models import DoctorSchedule, DoctorScheduleException
from .models import Appointment


def book_appointment(patient, doctor, date, start_time):

    exception = DoctorScheduleException.objects.filter(doctor=doctor, date=date).first()

    if exception:
        if exception.is_day_off:
            raise Exception("Doctor is off this day")

        schedule_start = exception.start_time
        schedule_end = exception.end_time
    else:
        day = date.strftime("%a").lower()[:3]

        schedule = DoctorSchedule.objects.filter(doctor=doctor, day_of_week=day).first()

        if not schedule:
            raise Exception("Doctor not working this day")

        schedule_start = schedule.start_time
        schedule_end = schedule.end_time

    duration = doctor.session_duration

    start_dt = datetime.combine(date, start_time)
    end_dt = start_dt + timedelta(minutes=duration)

    if not (schedule_start <= start_time < schedule_end):
        raise Exception("Invalid slot")

    if Appointment.objects.filter(
        doctor=doctor, appointment_date=date, start_time=start_time
    ).exists():
        raise Exception("Slot already booked")

    patient_appointments = Appointment.objects.filter(
        patient=patient,
        appointment_date=date,
        status__in=["requested", "confirmed", "checked_in"],
    )

    for appt in patient_appointments:
        appt_start = datetime.combine(date, appt.start_time)
        appt_end = datetime.combine(date, appt.end_time) + timedelta(
            minutes=appt.doctor.buffer_time
        )

        if start_dt < appt_end and end_dt > appt_start:
            raise Exception("You have overlapping appointment")

    with transaction.atomic():
        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            appointment_date=date,
            start_time=start_time,
            end_time=end_dt.time(),
            status="requested",
        )

    return appointment


def get_available_slots(doctor, selected_date):
    booked_slots = Appointment.objects.filter(
        doctor=doctor,
        appointment_date=selected_date,
        status__in=["requested", "confirmed", "checked_in", "no_show", "completed"],
    ).values_list("start_time", "end_time")

    booked_slots = list(booked_slots)
    day = selected_date.weekday()

    exceptions = DoctorScheduleException.objects.filter(
        doctor=doctor, date=selected_date
    )

    if exceptions.filter(is_day_off=True).exists():
        return []

    for exception in exceptions:
        if exception.start_time and exception.end_time:
            booked_slots.append((exception.start_time, exception.end_time))

    selected_day_schedule = DoctorSchedule.objects.filter(
        doctor=doctor, day_of_week=day
    ).first()

    if not selected_day_schedule:
        return []
    else:
        start_time = selected_day_schedule.start_time
        end_time = selected_day_schedule.end_time

    session_duration = doctor.session_duration
    buffer_time = doctor.buffer_time or 0

    current = datetime.combine(selected_date, start_time)
    end_datetime = datetime.combine(selected_date, end_time)

    slots = []

    while current + timedelta(minutes=session_duration) <= end_datetime:
        slot_start = current.time()
        slot_end = (current + timedelta(minutes=session_duration)).time()

        is_overlapping = False

        for booked_start, booked_end in booked_slots:
            if booked_start < slot_end and booked_end > slot_start:
                is_overlapping = True
                break

        if not is_overlapping:
            slots.append(
                {
                    "start": slot_start.strftime("%H:%M"),
                    "end": slot_end.strftime("%H:%M"),
                    "label": f"{slot_start.strftime('%I:%M %p')} - {slot_end.strftime('%I:%M %p')}",
                }
            )

        current += timedelta(minutes=session_duration + buffer_time)

    return slots
