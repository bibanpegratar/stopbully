from api.models import Post
from .models import Image
from rest_framework import serializers

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'