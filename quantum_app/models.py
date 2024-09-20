from django.db import models
import uuid


class KME(models.Model):
    kme_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source_KME_ID = models.CharField(max_length=255)
    target_KME_ID = models.CharField(max_length=255)
    key_size = models.IntegerField(default=256)
    stored_key_count = models.IntegerField(default=0)
    max_key_count = models.IntegerField(default=100000)
    max_key_per_request = models.IntegerField(default=128)
    min_key_size = models.IntegerField(default=64)
    max_key_size = models.IntegerField(default=1024)

    def __str__(self):
        return self.source_KME_ID


class SAE(models.Model):
    sae_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    kme_id = models.ForeignKey(KME, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class KeyMaterial(models.Model):
    key_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    kme_id = models.ForeignKey(KME, on_delete=models.CASCADE)
    key_value = models.CharField(max_length=512)
    key_size = models.IntegerField(default=256)
    status = models.CharField(max_length=50, default='active')

    def __str__(self):
        return str(self.key_id)
