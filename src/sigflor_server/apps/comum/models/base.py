from django.conf import settings
from django.db import models
from django.utils import timezone

from ..managers.softdelete import (
    SoftDeleteQuerySet
)

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True

class AuditModel(TimeStampedModel):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='created_%(class)ss',
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='updated_%(class)ss',
    )
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='deleted_%(class)ss',
    )
    class Meta:
        abstract = True

class SoftDeleteModel(AuditModel):
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    objects = SoftDeleteQuerySet.as_manager()

    class Meta:
        abstract = True

    def delete(self, user=None):
        self.deleted_at = timezone.now()
        self.updated_at = timezone.now()

        if getattr(self, 'principal', None) is not None:
            self.principal = False

        self.deleted_by = user
        self.updated_by = user
        self.save(update_fields=['deleted_at', 'updated_by', 'deleted_by', 'updated_at'])

    def hard_delete(self,):
        return super(models.Model, self).delete()

    def restore(self, user=None):
        self.deleted_at = None
        self.deleted_by = None
        self.updated_by = user
        self.save(update_fields=['deleted_by','deleted_at', 'updated_by', 'updated_at'])