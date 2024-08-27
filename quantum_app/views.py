from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView

from .models import KeyMaterial, SAE, KME, TrustedNode
from django.shortcuts import get_object_or_404
import uuid

from .serializers import SAESerializer, KeyMaterialSerializer, TrustedNodeSerializer, KMESerializer


class KeyViewSet(viewsets.ViewSet):

    @action(detail=True, methods=['get'], url_path='status')
    def get_status(self, request, slave_SAE_ID=None):
        """
        Vérifie le statut des clés disponibles pour le SAE esclave donné.
        """
        # Obtenez l'objet SAE correspondant à l'ID fourni
        slave_sae = get_object_or_404(SAE, sae_id=slave_SAE_ID)
        # Trouvez toutes les clés actives associées au KME de ce SAE
        keys = KeyMaterial.objects.filter(kme_id=slave_sae.kme_id, status='active')

        if keys.exists():
            return Response({
                'status': 'active',
                'available_keys': [key.key_id for key in keys],
                'message': 'Des clés sont disponibles pour ce SAE esclave.'
            }, status=status.HTTP_200_OK)

        return Response({
            'status': 'inactive',
            'message': 'Aucune clé active n\'est disponible pour ce SAE esclave.'
        }, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'], url_path='enc_keys')
    def get_enc_keys(self, request, slave_SAE_ID=None):
        """
        Obtient une nouvelle clé de chiffrement pour le SAE esclave donné.
        """
        # Obtenez l'objet SAE correspondant à l'ID fourni
        slave_sae = get_object_or_404(SAE, sae_id=slave_SAE_ID)
        # Simulez la génération d'une clé
        key_value = str(uuid.uuid4())
        # Créez un objet KeyMaterial associé à ce SAE
        key = KeyMaterial.objects.create(kme_id=slave_sae.kme_id, key_value=key_value)
        return Response({'key_id': key.key_id}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='dec_keys')
    def get_dec_keys(self, request, master_SAE_ID=None):
        """
        Récupère une clé de déchiffrement pour le SAE maître donné en fonction de l'identifiant de la clé.
        """
        # Obtenez l'identifiant de la clé fourni dans la requête
        key_id = request.data.get('key_id')
        # Obtenez l'objet KeyMaterial correspondant à l'ID fourni et au KME associé au SAE maître
        key = get_object_or_404(KeyMaterial, key_id=key_id, kme_id=master_SAE_ID, status='active')
        return Response({'key_value': key.key_value}, status=status.HTTP_200_OK)


class UserRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        if not username or not password:
            return Response({'error': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password)
        return Response({
            'message': 'User created successfully.',
            'user_id': user.id,
            'username': user.username},
            status=status.HTTP_201_CREATED)


class SAEViewSet(viewsets.ModelViewSet):
    queryset = SAE.objects.all()
    serializer_class = SAESerializer


class KMEViewSet(viewsets.ModelViewSet):
    queryset = KME.objects.all()
    serializer_class = KMESerializer


class KeyMaterialViewSet(viewsets.ModelViewSet):
    queryset = KeyMaterial.objects.all()
    serializer_class = KeyMaterialSerializer


class TrustedNodeViewSet(viewsets.ModelViewSet):
    queryset = TrustedNode.objects.all()
    serializer_class = TrustedNodeSerializer
