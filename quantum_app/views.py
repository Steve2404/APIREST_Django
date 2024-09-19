from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView

from .models import KeyMaterial, SAE, KME, TrustedNode
from django.shortcuts import get_object_or_404
import uuid

from .serializers import SAESerializer, KeyMaterialSerializer, TrustedNodeSerializer, KMESerializer
from .bb84 import generate_bb84_keys
import logging


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
                'available_keys_id': [key.key_id for key in keys],
                'available_keys': [key.key_value for key in keys],
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


logger = logging.getLogger(__name__)


@api_view(['POST'])
def generate_keys(request, sae_id):
    try:
        logger.info(f"Requête de génération de clés reçue pour SAE ID: {sae_id}")

        num_keys = request.data.get('num_keys', 3)
        num_bits_per_key = request.data.get('num_bits_per_key', 10)
        logger.info(f"Nombre de clés demandé: {num_keys}")

        token = ""
        keys = generate_bb84_keys(num_keys, num_bits_per_key, token)

        if not keys:
            logger.error("Erreur lors de la génération des clés")
            return Response({"message": "Erreur lors de la génération des clés"}, status=500)

        logger.info("Clés générées avec succès")

        # Récupérer l'instance de KME correspondante au SAE_ID
        kme = get_object_or_404(KME, kme_id=sae_id)

        # Stocker les clés générées dans la base de données en format natif
        for key in keys:
            key_str = ','.join(map(str, key))  # Convertit la liste d'entiers en chaîne de caractères
            KeyMaterial.objects.create(kme_id=kme, key_value=key_str, status='active')

        return Response({"message": "Clés générées avec succès", "keys": keys}, status=200)

    except Exception as e:
        logger.exception("Une erreur s'est produite")
        return Response({"message": "Erreur interne du serveur"}, status=500)


@api_view(['GET'])
def get_keys_for_bob(request, sae_id):
    """Récupérer les clés générées pour Bob"""
    # Récupérer l'entité SAE de Bob
    bob_sae = SAE.objects.get(sae_id=sae_id)

    # Rechercher les clés qui sont générées pour Bob dans la base de données
    keys = KeyMaterial.objects.filter(kme_id=bob_sae.kme_id, status='active')

    if not keys.exists():
        return Response({"message": "Aucune clé trouvée pour Bob"}, status=404)
    print(keys)
    # Renvoie les clés sous forme de réponse JSON
    return Response({"keys": [key.key_value for key in keys]})


@api_view(['POST'])
def get_key_with_id(request, master_SAE_ID):
    """Obtenir une clé en utilisant son identifiant pour Bob"""
    key_id = request.data.get('key_id')
    key = KeyMaterial.objects.get(id=key_id, kme_id=master_SAE_ID, status='active')

    if not key:
        return Response({"message": "Clé introuvable ou inactive"}, status=404)

    return Response({"key_value": key.key_value})


@api_view(['POST'])
def compare_bases_and_calculate_qber(request):
    """Comparer les bases d'Alice et Bob et calculer le QBER"""
    # Obtenir les bases et les clés d'Alice et de Bob depuis la requête
    alice_basis = request.data.get('alice_basis')
    bob_basis = request.data.get('bob_basis')
    alice_key = request.data.get('alice_key')
    bob_key = request.data.get('bob_key')

    if not alice_basis or not bob_basis or not alice_key or not bob_key:
        return Response({"message": "Données manquantes pour la comparaison des bases"}, status=400)

    # Calculer le QBER (Quantum Bit Error Rate)
    errors = sum(1 for a, b in zip(alice_key, bob_key) if a != b)
    qber = errors / len(alice_key) if len(alice_key) > 0 else 0

    # Vérifier si le QBER est acceptable pour continuer l'échange de clé
    if qber > 0.1:
        return Response({"message": "Erreur élevée, abandon de la clé", "qber": qber}, status=400)

    return Response({"message": "Clé valide, QBER acceptable", "qber": qber})
