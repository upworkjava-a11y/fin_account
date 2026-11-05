from django.db import models


class EriLogin(models.Model):
    cn = models.CharField(max_length=255, blank=True)
    stir = models.CharField(max_length=9, blank=True)
    pinfl = models.CharField(max_length=14, blank=True)
    serial = models.CharField(max_length=128, blank=True)
    verified_by = models.CharField(max_length=32)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.stir or self.pinfl or self.cn or str(self.pk)
