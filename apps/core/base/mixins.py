"""
SyncRH - Mixins
===============

Mixins reutilizáveis para views, serializers e models.
"""

from django.db import models
from django.utils import timezone
import uuid


class TimestampMixin(models.Model):
    """Mixin para campos de timestamp"""
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Criado em'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizado em'
    )

    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    """Mixin para adicionar UUID único"""
    
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True,
        verbose_name='UUID'
    )

    class Meta:
        abstract = True


class SoftDeleteMixin(models.Model):
    """Mixin para soft delete"""
    
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name='Ativo'
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Excluído em'
    )

    class Meta:
        abstract = True

    def soft_delete(self):
        """Realiza exclusão lógica"""
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_active', 'deleted_at', 'updated_at'])

    def restore(self):
        """Restaura registro excluído"""
        self.is_active = True
        self.deleted_at = None
        self.save(update_fields=['is_active', 'deleted_at', 'updated_at'])


class AuditMixin(models.Model):
    """Mixin para auditoria"""
    
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(app_label)s_%(class)s_created',
        verbose_name='Criado por'
    )
    updated_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(app_label)s_%(class)s_updated',
        verbose_name='Atualizado por'
    )

    class Meta:
        abstract = True
