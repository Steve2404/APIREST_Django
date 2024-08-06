from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission


class User(AbstractUser):
    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )


class KeyMaterial(models.Model):
    kme_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='keys')
    key_value = models.TextField()
    creation_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='active')


class KeyRequest(models.Model):
    master_sae_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='key_requests_made')
    slave_sae_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='key_requests_received')
    requested_key_count = models.IntegerField()
    requested_key_size = models.IntegerField()
    request_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending')


class KeyDelivery(models.Model):
    request_id = models.ForeignKey(KeyRequest, on_delete=models.CASCADE)
    key_id = models.ForeignKey(KeyMaterial, on_delete=models.CASCADE)
    delivery_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='delivered')
