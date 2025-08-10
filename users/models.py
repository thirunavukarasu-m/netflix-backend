from django.db import models
from django.contrib.auth.models import AbstractUser

class Users(AbstractUser):
    ROLES = (
        ('user', 'User'),
        ('admin', 'Admin'),
        ('tester', 'Tester'),
    )
    email = models.EmailField(unique=True)
    roles = models.CharField(max_length=6, default='user', choices=ROLES)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

