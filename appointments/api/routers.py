from rest_framework.routers import DefaultRouter
from .views import AppointmentViewSet

router = DefaultRouter()
router.register(r'appointments_view', AppointmentViewSet, basename='appointments_view')