from rest_framework import serializers
from .models import User, KeyMaterial, KeyRequest, KeyDelivery
from django.contrib.auth.hashers import make_password


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)


class KeyMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = KeyMaterial
        fields = '__all__'


class KeyRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = KeyRequest
        fields = '__all__'


class KeyDeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = KeyDelivery
        fields = '__all__'
