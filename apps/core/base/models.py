"""
SyncRH - Models Base
====================

Classes base para todos os models da aplicação.
Implementa padrões de segurança, auditoria e soft delete.
"""

import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class UUIDMixin(models.Model):
    """Mixin para adicionar UUID único aos models"""
    
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True,
        verbose_name='UUID',
        help_text='Identificador único universal'
    )

    class Meta:
        abstract = True


class TimestampMixin(models.Model):
    """Mixin para campos de timestamp"""
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Criado em',
        help_text='Data e hora de criação do registro'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizado em',
        help_text='Data e hora da última atualização'
    )

    class Meta:
        abstract = True


class SoftDeleteMixin(models.Model):
    """Mixin para soft delete (exclusão lógica)"""
    
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name='Ativo',
        help_text='Indica se o registro está ativo'
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Excluído em',
        help_text='Data e hora da exclusão lógica'
    )

    class Meta:
        abstract = True

    def soft_delete(self):
        """Realiza exclusão lógica do registro"""
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_active', 'deleted_at', 'updated_at'])

    def restore(self):
        """Restaura registro excluído logicamente"""
        self.is_active = True
        self.deleted_at = None
        self.save(update_fields=['is_active', 'deleted_at', 'updated_at'])


class AuditMixin(models.Model):
    """Mixin para auditoria de criação e modificação"""
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(app_label)s_%(class)s_created',
        verbose_name='Criado por',
        help_text='Usuário que criou o registro'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(app_label)s_%(class)s_updated',
        verbose_name='Atualizado por',
        help_text='Usuário que atualizou o registro'
    )

    class Meta:
        abstract = True


class BaseModel(UUIDMixin, TimestampMixin, SoftDeleteMixin, models.Model):
    """
    Modelo base para todos os models da aplicação.
    
    Inclui:
    - UUID único
    - Timestamps de criação e atualização
    - Soft delete
    
    Uso:
        class MeuModel(BaseModel):
            nome = models.CharField(max_length=100)
    """
    
    id = models.BigAutoField(primary_key=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def __repr__(self):
        return f'<{self.__class__.__name__} pk={self.pk}>'


class AuditModel(BaseModel, AuditMixin):
    """
    Modelo base com auditoria completa.
    
    Inclui tudo do BaseModel mais:
    - Campos de auditoria (created_by, updated_by)
    
    Uso:
        class MeuModel(AuditModel):
            nome = models.CharField(max_length=100)
    """

    class Meta:
        abstract = True
        ordering = ['-created_at']
