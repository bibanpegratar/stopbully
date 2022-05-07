from re import S
from django.db import models

# Create your models here.
class Image(models.Model):
    user_id = models.ForeignKey('api.CustomUser', on_delete=models.CASCADE, db_column='user_id')
    image = models.ImageField(upload_to='images/', blank=True)
    has_face = models.BooleanField(default=False)