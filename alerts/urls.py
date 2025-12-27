# alerts/urls.py
from django.urls import path
from .views import iot_alert

urlpatterns = [
    path("api/iot-alert/", iot_alert),
]
