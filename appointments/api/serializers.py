from rest_framework import serializers
from appointments.models import Appointment, RescheduleRequest
from doctors.models import DoctorProfile

class RescheduleRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RescheduleRequest
        fields = '__all__'

class AppointmentSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source='doctor.user.get_full_name', read_only=True)
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    reschedule_requests = RescheduleRequestSerializer(source='reschedulerequest_set', many=True, read_only=True)

    class Meta:
        model = Appointment
        fields = '__all__'
        



class PatientAppointmentSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source='doctor.user.get_full_name', read_only=True)

    class Meta:
        model  = Appointment
        fields = ["id", "doctor_name", "appointment_date", "start_time", "status", "created_at"]


class PatientBookAppointmentSerializer(serializers.Serializer):
    doctor_id = serializers.IntegerField()
    date      = serializers.DateField()
    time      = serializers.TimeField(input_formats=["%I:%M %p", "%H:%M"])

    def validate_date(self, value):
        from datetime import date
        if value < date.today():
            raise serializers.ValidationError("Cannot book a past date.")
        return value

    def validate_doctor_id(self, value):
        if not DoctorProfile.objects.filter(id=value).exists():
            raise serializers.ValidationError("Doctor not found.")
        return value


class PatientRescheduleSerializer(serializers.Serializer):
    date = serializers.DateField()
    time = serializers.TimeField(input_formats=["%I:%M %p", "%H:%M"])

    def validate_date(self, value):
        from datetime import date
        if value < date.today():
            raise serializers.ValidationError("Cannot reschedule to a past date.")
        return value
