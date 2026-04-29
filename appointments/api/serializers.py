from rest_framework import serializers
from appointments.models import Appointment, RescheduleRequest

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
