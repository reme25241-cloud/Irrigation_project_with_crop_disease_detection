# alerts/admin.py
from django.contrib import admin
from .models import IoTAlert

@admin.register(IoTAlert)
class IoTAlertAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "relay",
        "temperature",
        "humidity",
        "soil_value",
        "alert_triggered",
        "created_at",
    )
    list_filter = ("alert_triggered", "relay")
    search_fields = ("relay",)
