# alerts/urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path("api/iot-alert/", iot_alert, name="iot_alert"),
    path("alert_dashboard/", alert_dashboard, name="alert_dashboard"),
]
