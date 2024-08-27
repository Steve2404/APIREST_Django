"""
URL configuration for QuantAPI project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from quantum_app.views import KeyViewSet, UserRegistrationView, SAEViewSet, KMEViewSet, KeyMaterialViewSet, \
    TrustedNodeViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r'saes', SAEViewSet)
router.register(r'kmes', KMEViewSet)
router.register(r'keymaterials', KeyMaterialViewSet)
router.register(r'trustednodes', TrustedNodeViewSet)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
    path('api/v1/keys/', include([
        path('<str:slave_SAE_ID>/status/', KeyViewSet.as_view({'get': 'get_status'}), name='get_status'),
        path('<str:slave_SAE_ID>/enc_keys/', KeyViewSet.as_view({'post': 'get_enc_keys'}), name='get_enc_keys'),
        path('<str:master_SAE_ID>/dec_keys/', KeyViewSet.as_view({'post': 'get_dec_keys'}), name='get_dec_keys'),
    ])),
    path('api/auth/register/', UserRegistrationView.as_view(), name='register_user'),
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh')
]
