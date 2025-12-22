# users/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required

from django.db.models import Q
from django.conf import settings

from django.contrib.auth import get_user_model

from .forms import *
from .models import *

def base(request):
    return render(request, 'base.html')

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')  # Redirect to dashboard after signup
        else:
            # If form is not valid, it will pass validation errors back to the template
            return render(request, 'registration/signup.html', {'form': form})
    else:
        form = CustomUserCreationForm()
    
    # If the form is accessed via GET (for example, on initial page load)
    return render(request, 'registration/signup.html', {'form': form})


# Handle user logout
def logout_view(request):
    logout(request)
    return redirect('login')

# profile
@login_required
def profile_view(request):
    return render(request, 'account/profile.html', {'user': request.user})

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm

@login_required
def edit_profile(request):
    user = request.user  # Get the current logged-in user

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=user)  # Pre-fill the form with user's current data
        if form.is_valid():
            form.save()  # Save the updated data to the database
            return redirect('profile')  # Redirect to profile page (or dashboard, etc.)
    else:
        form = ProfileForm(instance=user)  # Display the form with user's current data

    return render(request, 'account/edit_profile.html', {'form': form})


# dashboard
User = get_user_model()  # Refers to CustomUser

@login_required
def dashboard(request):
    predictions = DiseasePrediction.objects.all().order_by('-created_at')
    return render(request, 'dashboard/dashboard.html', {'predictions': predictions})



def about(request):
    return render(request, 'about/about.html')

# chat
@login_required
def user_list_view(request):
    users = get_user_model().objects.exclude(id=request.user.id)  
    return render(request, 'users/user_list.html', {'users': users})


@login_required
def chat_view_by_id(request, user_id):
    other_user = get_object_or_404(CustomUser, id=user_id)
    messages = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=other_user)) |
        (Q(sender=other_user) & Q(receiver=request.user))
    ).order_by('timestamp')

    if request.method == 'POST':
        text = request.POST.get('text')
        image = request.FILES.get('image')
        Message.objects.create(sender=request.user, receiver=other_user, text=text, image=image)
        return redirect('chat', user_id=other_user.id)  # ✅ Corrected: use user_id instead of username

    return render(request, 'users/chat.html', {
        'messages': messages,
        'receiver': other_user
    })

# Feedback

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import FeedbackForm
from .models import Feedback

@login_required
def feedback_view(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.save()
            return render(request, 'feedback/feedback_thanks.html')  # Create this template
    else:
        form = FeedbackForm()
    return render(request, 'feedback/feedback.html', {'form': form})

@login_required
def view_feedbacks(request):
    if request.user.is_superuser:
        feedbacks = Feedback.objects.all().order_by('-created_at')
        return render(request, 'feedback/view_feedbacks.html', {'feedbacks': feedbacks})
    else:
        return redirect('dashboard')

# myapp/views.py
# myapp/views.py

# views.py
# myapp/views.py
import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import DiseasePrediction


# @csrf_exempt
# def save_prediction(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)

#             DiseasePrediction.objects.create(
#                 disease_name=data.get('disease_name', ''),
#                 cause=data.get('cause', ''),
#                 symptoms=data.get('symptoms', ''),
#                 transmission=data.get('transmission', ''),
#                 prevention=data.get('prevention', ''),
#                 treatment=data.get('treatment', ''),
#                 impact=data.get('impact', ''),
#                 notes=data.get('notes', '')
#             )

#             return JsonResponse({'status': 'success'})
#         except Exception as e:
#             return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

#     return JsonResponse({'status': 'invalid method'}, status=405)





#  ------------------- mail --------------------
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings

@csrf_exempt
def save_prediction(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            prediction = DiseasePrediction.objects.create(
                disease_name=data.get('disease_name', ''),
                cause=data.get('cause', ''),
                symptoms=data.get('symptoms', ''),
                transmission=data.get('transmission', ''),
                prevention=data.get('prevention', ''),
                treatment=data.get('treatment', ''),
                impact=data.get('impact', ''),
                notes=data.get('notes', '')
            )

            # 📧 Email content
            subject = f"New Disease Prediction: {prediction.disease_name}"
            message = f"""
                A new prediction has been made.

                Name: {prediction.disease_name}

                Cause:
                {prediction.cause}

                Symptoms:
                {prediction.symptoms}

                Transmission:
                {prediction.transmission}

                Prevention:
                {prediction.prevention}

                Treatment:
                {prediction.treatment}

                Impact:
                {prediction.impact}

                Notes:
                {prediction.notes}
                            """

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                ['admin@example.com'],  # receiver email(s)
                fail_silently=False,
            )

            return JsonResponse({'status': 'success'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'invalid method'}, status=405)


# -------------------------------------------------------------------

@login_required
def predict(request):
    """Prediction form page"""
    return render(request, 'predict/form.html')



@login_required
def predict_live_input(request):
    """Prediction form page"""
    return render(request, 'predict/form_camera.html')

