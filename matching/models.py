from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    pass 

class Interest(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    interests = models.ManyToManyField(Interest, blank=True)
    phone = models.CharField(max_length=20, blank=False, unique=True, db_index=True)
    email = models.EmailField(max_length=100, blank=False, unique=True, db_index=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=False)
    country = models.CharField(max_length=100, blank=False)
    online = models.BooleanField(default=True)
    chat_room = models.CharField(max_length=255, null=True, blank=True)
    searching = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

