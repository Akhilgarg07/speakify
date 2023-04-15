from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .decorators import user_is_not_authenticated
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from .models import UserProfile
from django.contrib import messages
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.db import transaction
from django.contrib import messages

@user_is_not_authenticated(login_url='/dashboard/')
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create UserProfile
            phone_number = form.cleaned_data.get('phone')
            country_code = form.cleaned_data.get('country_code')
            email = form.cleaned_data.get('email')
            gender = form.cleaned_data.get('gender')
            country = form.cleaned_data.get('country')
            interests = form.cleaned_data.get('interests', []) # Set a default empty list if no interests are selected
            phone = '+{}{}'.format(country_code, phone_number)
            user_profile = UserProfile(user=user, phone=phone, email=email, gender=gender, country=country)
            user_profile.save()
            user_profile.interests.set(interests)
            # Log the user in
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            return redirect('matching:dashboard')
        else:
            messages.error(request, 'Registration failed. Please check your input.')
            print("Form errors:", form.errors)
    else:
        form = CustomUserCreationForm()
    return render(request, 'matching/register.html', {'form': form})


@user_is_not_authenticated(login_url='/dashboard/')
def login_view(request):
    if request.method == 'POST':
        identifier = request.POST['identifier']
        password = request.POST['password']
        user = authenticate(request, username=identifier, password=password)
        if user is not None:
            login(request, user)
            return redirect('matching:dashboard')
        else:
            messages.error(request, 'Invalid email/phone or password.')
    return render(request, 'matching/login.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('matching:login')

@login_required
def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('matching:login')

    user_profile = UserProfile.objects.get(user=request.user)
    is_online = user_profile.online

    return render(request, 'matching/dashboard.html', {'is_online': is_online})


def update_online_status(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'User is not authenticated'})

    user_profile = UserProfile.objects.get(user=request.user)
    user_profile.online = not user_profile.online
    user_profile.save()

    return JsonResponse({'status': 'success', 'is_online': user_profile.online})

def find_matching_user(current_user):
    user_profile = UserProfile.objects.get(user=current_user)
    users_online = UserProfile.objects.filter(
        online=True,
        chat_room=None,
    ).exclude(user=current_user)
    matched_users = users_online.filter(interests__in=user_profile.interests.all())
    
    if not matched_users.exists():
        matched_users = users_online
    
    if matched_users.exists():
        return matched_users.first().user
    return None


def find_match(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'User is not authenticated'})


    match = find_matching_user(request.user)
    if match:
        room_name = f"{min(request.user.id, match.id)}_{max(request.user.id, match.id)}"
        
        with transaction.atomic():
            user_profile = UserProfile.objects.select_for_update().get(user=request.user)
            match_profile = UserProfile.objects.select_for_update().get(user=match)
            match_profile.chat_room = room_name
            match_profile.save()
        
        return JsonResponse({'status': 'success', 'room_name': room_name})
    else:
        return JsonResponse({'status': 'error', 'message': 'No matching users found'})
