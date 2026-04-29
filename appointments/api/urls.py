from django.urls import path, include
from .routers import router
from .views import available_slots

urlpatterns = [
    path('', include(router.urls)),
    path('slots/', available_slots, name='available_slots_api'),
]
