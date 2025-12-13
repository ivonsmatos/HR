"""
SyncRH - Validadores
====================

Validadores customizados para campos de formulários e models.
Implementa validações específicas para o contexto brasileiro.
"""

import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_cpf(value: str) -> None:
    """
    Valida CPF brasileiro.
    
    Args:
        value: CPF a ser validado (com ou sem formatação)
        
    Raises:
        ValidationError: Se o CPF for inválido
    """
    # Remove caracteres não numéricos
    cpf = re.sub(r'[^0-9]', '', str(value))
    
    if len(cpf) != 11:
        raise ValidationError(
            _('CPF deve conter 11 dígitos.'),
            code='invalid_cpf_length'
        )
    
    # Verifica se todos os dígitos são iguais
    if cpf == cpf[0] * 11:
        raise ValidationError(
            _('CPF inválido.'),
            code='invalid_cpf'
        )
    
    # Validação do primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    
    if int(cpf[9]) != digito1:
        raise ValidationError(
            _('CPF inválido.'),
            code='invalid_cpf'
        )
    
    # Validação do segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto
    
    if int(cpf[10]) != digito2:
        raise ValidationError(
            _('CPF inválido.'),
            code='invalid_cpf'
        )


def validate_cnpj(value: str) -> None:
    """
    Valida CNPJ brasileiro.
    
    Args:
        value: CNPJ a ser validado (com ou sem formatação)
        
    Raises:
        ValidationError: Se o CNPJ for inválido
    """
    # Remove caracteres não numéricos
    cnpj = re.sub(r'[^0-9]', '', str(value))
    
    if len(cnpj) != 14:
        raise ValidationError(
            _('CNPJ deve conter 14 dígitos.'),
            code='invalid_cnpj_length'
        )
    
    # Verifica se todos os dígitos são iguais
    if cnpj == cnpj[0] * 14:
        raise ValidationError(
            _('CNPJ inválido.'),
            code='invalid_cnpj'
        )
    
    # Validação do primeiro dígito verificador
    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj[i]) * pesos1[i] for i in range(12))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    
    if int(cnpj[12]) != digito1:
        raise ValidationError(
            _('CNPJ inválido.'),
            code='invalid_cnpj'
        )
    
    # Validação do segundo dígito verificador
    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj[i]) * pesos2[i] for i in range(13))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto
    
    if int(cnpj[13]) != digito2:
        raise ValidationError(
            _('CNPJ inválido.'),
            code='invalid_cnpj'
        )


def validate_phone(value: str) -> None:
    """
    Valida telefone brasileiro.
    
    Args:
        value: Telefone a ser validado
        
    Raises:
        ValidationError: Se o telefone for inválido
    """
    # Remove caracteres não numéricos
    phone = re.sub(r'[^0-9]', '', str(value))
    
    if len(phone) < 10 or len(phone) > 11:
        raise ValidationError(
            _('Telefone deve conter 10 ou 11 dígitos.'),
            code='invalid_phone'
        )
    
    # Valida DDD (11-99)
    ddd = int(phone[:2])
    if ddd < 11 or ddd > 99:
        raise ValidationError(
            _('DDD inválido.'),
            code='invalid_ddd'
        )


def validate_cep(value: str) -> None:
    """
    Valida CEP brasileiro.
    
    Args:
        value: CEP a ser validado
        
    Raises:
        ValidationError: Se o CEP for inválido
    """
    # Remove caracteres não numéricos
    cep = re.sub(r'[^0-9]', '', str(value))
    
    if len(cep) != 8:
        raise ValidationError(
            _('CEP deve conter 8 dígitos.'),
            code='invalid_cep'
        )


def validate_positive(value) -> None:
    """
    Valida se valor é positivo.
    
    Args:
        value: Valor a ser validado
        
    Raises:
        ValidationError: Se o valor for negativo
    """
    if value < 0:
        raise ValidationError(
            _('O valor deve ser positivo.'),
            code='negative_value'
        )


def validate_percentage(value) -> None:
    """
    Valida se valor é uma porcentagem válida (0-100).
    
    Args:
        value: Valor a ser validado
        
    Raises:
        ValidationError: Se o valor não estiver entre 0 e 100
    """
    if value < 0 or value > 100:
        raise ValidationError(
            _('O valor deve estar entre 0 e 100.'),
            code='invalid_percentage'
        )


def validate_pis(value: str) -> None:
    """
    Valida PIS/PASEP brasileiro.
    
    Args:
        value: PIS a ser validado
        
    Raises:
        ValidationError: Se o PIS for inválido
    """
    # Remove caracteres não numéricos
    pis = re.sub(r'[^0-9]', '', str(value))
    
    if len(pis) != 11:
        raise ValidationError(
            _('PIS deve conter 11 dígitos.'),
            code='invalid_pis_length'
        )
    
    pesos = [3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(pis[i]) * pesos[i] for i in range(10))
    resto = soma % 11
    digito = 0 if resto < 2 else 11 - resto
    
    if int(pis[10]) != digito:
        raise ValidationError(
            _('PIS inválido.'),
            code='invalid_pis'
        )
