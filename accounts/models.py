from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager
import os

def file_upload_path(instance, filename):
    return 'uploads/'+ str(instance.user.id) + '/' + filename

class CustomUser(AbstractUser):
    username = None
    first_name = models.CharField(max_length=100,blank=True,null=True)
    last_name = models.CharField(max_length=100,blank=True,null=True)
    email = models.EmailField('Email Address', unique=True)
    mobile = models.CharField(max_length=14, unique=True)
    is_ops_user = models.BooleanField(default=False)
    signup_token = models.CharField(max_length=255, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['mobile', 'first_name', 'last_name']

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class File(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="files")
    file = models.FileField(upload_to=file_upload_path)
    file_type = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


