import uuid

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import User, KeyMaterial, KeyRequest, KeyDelivery
from .serializers import UserSerializer, KeyMaterialSerializer, KeyRequestSerializer, KeyDeliverySerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=['post'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        if user := authenticate(username=username, password=password):
            refresh = RefreshToken.for_user(user)
            return Response({'refresh': str(refresh), 'access': str(refresh.access_token)})
        else:
            return Response({'error': 'Invalid Credentials'}, status=400)


class KeyMaterialViewSet(viewsets.ModelViewSet):
    queryset = KeyMaterial.objects.all()
    serializer_class = KeyMaterialSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def generate_key(self, request):
        user = request.user
        key_value = str(uuid.uuid4())  # This should be a real key value generated securely
        key_material = KeyMaterial(kme_id=user, key_value=key_value)
        key_material.save()
        return Response({'key_id': key_material.id})


class KeyRequestViewSet(viewsets.ModelViewSet):
    queryset = KeyRequest.objects.all()
    serializer_class = KeyRequestSerializer
    permission_classes = [IsAuthenticated]


class KeyDeliveryViewSet(viewsets.ModelViewSet):
    queryset = KeyDelivery.objects.all()
    serializer_class = KeyDeliverySerializer
    permission_classes = [IsAuthenticated]
