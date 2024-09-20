from django.contrib.auth.models import User
from rest_framework import serializers
from .models import KeyMaterial, SAE, KME
from django.contrib.auth.hashers import make_password


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)


class SAESerializer(serializers.ModelSerializer):
    class Meta:
        model = SAE
        fields = '__all__'


class KeyMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = KeyMaterial
        fields = '__all__'


class KMESerializer(serializers.ModelSerializer):
    class Meta:
        model = KME
        fields = '__all__'
