# alerts/views.py
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings

@csrf_exempt
def iot_alert(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    data = json.loads(request.body)

    soil = data.get("soil")
    temperature = data.get("temperature")
    relay = data.get("relay")

    # ---- Alert conditions ----
    if temperature > 40 or relay == "ON":
        send_mail(
            subject="🚨 Smart Agriculture Alert",
            message=f"""
Temperature: {temperature} °C
Soil Value: {soil}
Relay Status: {relay}

Immediate action recommended.
""",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=["your_email@gmail.com"],
            fail_silently=False,
        )

    return JsonResponse({"status": "alert processed"})
