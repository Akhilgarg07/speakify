import pycountry
import phonenumbers
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile, Interest

from phonenumbers import COUNTRY_CODE_TO_REGION_CODE

PHONE_CODE_CHOICES = [
    (code, f"+{code}") for code in sorted(COUNTRY_CODE_TO_REGION_CODE.keys())
]# COUNTRY_CODE_CHOICES = [(country.alpha_2, '+{} ({})'.format(country.phone_code, country.alpha_2)) for country in pycountry.countries]

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    COUNTRY_CHOICES = [(country.alpha_2, country.name) for country in pycountry.countries]
    country_code = forms.ChoiceField(choices=PHONE_CODE_CHOICES, required=True)
    phone = forms.CharField(max_length=20, required=True, help_text='Enter your phone number without the country code')
    gender = forms.ChoiceField(choices=UserProfile.GENDER_CHOICES, required=True)
    country = forms.ChoiceField(choices=[(country.name, country.name) for country in pycountry.countries], required=True)
    interests = forms.ModelMultipleChoiceField(
        queryset=Interest.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')

    def clean_phone(self):
        country_code = self.cleaned_data.get('country_code')
        phone = self.cleaned_data.get('phone')
        phone_number = '+{}{}'.format(country_code, phone)
        if UserProfile.objects.filter(phone=phone_number).exists():
            raise ValidationError(_('This phone number is already in use.'))
        try:
            parsed_number = phonenumbers.parse(phone_number)
            if not phonenumbers.is_valid_number(parsed_number):
                raise ValidationError(_('Invalid phone number.'))
        except phonenumbers.NumberParseException:
            raise ValidationError(_('Invalid phone number.'))
        return phone
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError(_('This email address is already in use.'))
        return email
    
    def save(self, commit=True):
        user = super(CustomUserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.username = user.email  # Set the username to the email address
        if commit:
            user.save()
        return user
