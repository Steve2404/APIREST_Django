from django.db import models
import uuid


class SAE(models.Model):
    sae_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    kme_id = models.ForeignKey('KME', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class KME(models.Model):
    kme_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class KeyMaterial(models.Model):
    key_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    kme_id = models.ForeignKey(KME, on_delete=models.CASCADE)
    key_value = models.CharField(max_length=512)
    status = models.CharField(max_length=50, default='active')

    def __str__(self):
        return str(self.key_id)


class TrustedNode(models.Model):
    trusted_node_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    location = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.location
