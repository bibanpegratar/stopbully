from .models import Image
from rest_framework import serializers

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'

class ImageDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        exclude = ['image']