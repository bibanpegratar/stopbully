from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

class CustomUser(AbstractUser):
    email = models.EmailField('email address', unique=True)
    # username = None
    usermame = models.CharField(max_length=250, null=True, unique=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

@receiver(post_save, sender = settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance = None, created = False, **kwargs):
    if created:
        Token.objects.create(user=instance)

class Post(models.Model):
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column='user_id')
    caption = models.CharField(max_length=250, default='')
    content = models.CharField(max_length=2500, default='')
    likes = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True, null=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, null=True, editable=False)

    def __str__(self):
        return self.caption

class Comment(models.Model):
    post_id = models.ForeignKey('Post', on_delete=models.CASCADE, db_column='post_id')
    content = models.CharField(max_length=500, default='')
    likes = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True, null=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, null=True, editable=False)

    def __str__(self):
        return self.content