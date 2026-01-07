# alerts/views.py
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from .models import IoTAlert

@csrf_exempt
def iot_alert(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    soil = data.get("soil")
    temperature = data.get("temperature")
    humidity = data.get("humidity")
    relay = data.get("relay")

    if temperature is None or relay is None:
        return JsonResponse({"error": "Missing required fields"}, status=400)

    # ---- Alert condition ----
    alert_triggered = temperature > 40 or relay != "Relay 0"
    print(alert_triggered)

    # ---- Save to DB ----
    alert = IoTAlert.objects.create(
        soil_value=soil,
        temperature=temperature,
        humidity=humidity,
        relay=relay,
        alert_triggered=alert_triggered
    )

    # ---- Send Email ----
    if alert_triggered:
        send_mail(
            subject="🚨 Smart Agriculture Alert",
            message=f"""
Temperature: {temperature} °C
Humidity: {humidity} %
Soil Value: {soil}
Relay: {relay}

Immediate action recommended.
""",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=["your_email@gmail.com"],
            fail_silently=False,
        )

    return JsonResponse({
        "status": "saved",
        "alert": alert_triggered,
        "id": alert.id
    })

from django.shortcuts import render
from .models import IoTAlert

from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings

from .models import IoTAlert


def alert_dashboard(request):
    alerts = IoTAlert.objects.all().order_by("-created_at")

    context = {
        "alerts": alerts,
        "total_alerts": alerts.count(),
        "critical_alerts": alerts.filter(alert_triggered=True).count(),
    }

    return render(request, "alerts/alert_dashboard.html", context)




