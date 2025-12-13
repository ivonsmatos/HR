"""
SyncRH - Módulo Base
====================

Este módulo contém classes base, mixins, validadores e utilitários
compartilhados por todos os módulos da aplicação.
"""

from apps.core.base.models import BaseModel, AuditModel
from apps.core.base.validators import (
    validate_cpf,
    validate_cnpj,
    validate_phone,
    validate_cep,
)
from apps.core.base.mixins import (
    TimestampMixin,
    UUIDMixin,
    SoftDeleteMixin,
    AuditMixin,
)

__all__ = [
    'BaseModel',
    'AuditModel',
    'validate_cpf',
    'validate_cnpj',
    'validate_phone',
    'validate_cep',
    'TimestampMixin',
    'UUIDMixin',
    'SoftDeleteMixin',
    'AuditMixin',
]
