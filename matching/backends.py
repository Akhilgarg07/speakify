from django.contrib.auth.backends import BaseBackend
from .models import User, UserProfile

class PhoneEmailBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Check if the provided identifier is an email address
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            try:
                # If not an email, check for a phone number
                if not username.startswith('+'):
                    username = '+' + username
                user_profile = UserProfile.objects.get(phone=username)
                user = user_profile.user
            except UserProfile.DoesNotExist:
                # Return None if no user found with the given email or phone
                return None

        if user.check_password(password):
            return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
