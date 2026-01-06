from django.db import models

class IoTAlert(models.Model):
    soil_value = models.IntegerField(null=True, blank=True)
    temperature = models.FloatField()
    humidity = models.FloatField(null=True, blank=True)
    relay = models.CharField(max_length=20)
    alert_triggered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.relay} | {self.temperature}°C | {self.created_at}"
