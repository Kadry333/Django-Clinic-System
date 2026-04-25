from datetime import datetime, timedelta
from django.db import transaction
from doctors.models import DoctorSchedule, DoctorScheduleException
from .models import Appointment


def book_appointment(patient, doctor, date, start_time):


    exception = DoctorScheduleException.objects.filter(
        doctor=doctor,
        date=date
    ).first()

    if exception:
        if exception.is_day_off:
            raise Exception("Doctor is off this day")

        schedule_start = exception.start_time
        schedule_end = exception.end_time
    else:
        day = date.strftime('%a').lower()[:3]

        schedule = DoctorSchedule.objects.filter(
            doctor=doctor,
            day_of_week=day
        ).first()

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
        doctor=doctor,
        appointment_date=date,
        start_time=start_time
    ).exists():
        raise Exception("Slot already booked")


    patient_appointments = Appointment.objects.filter(
        patient=patient,
        appointment_date=date,
        status__in=["requested", "confirmed", "checked_in"]
    )

    for appt in patient_appointments:
        appt_start = datetime.combine(date, appt.start_time)
        appt_end = datetime.combine(date, appt.end_time) + timedelta(minutes=appt.doctor.buffer_time)

        if start_dt < appt_end and end_dt > appt_start:
            raise Exception("You have overlapping appointment")

  
    with transaction.atomic():
        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            appointment_date=date,
            start_time=start_time,
            end_time=end_dt.time(),
            status='requested'
        )

    return appointment



