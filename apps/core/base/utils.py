"""
SyncRH - Utilitários
====================

Funções utilitárias compartilhadas por toda a aplicação.
"""

import re
import hashlib
from typing import Optional
from datetime import date, datetime
from decimal import Decimal


def format_cpf(cpf: str) -> str:
    """
    Formata CPF com pontos e traço.
    
    Args:
        cpf: CPF sem formatação
        
    Returns:
        CPF formatado (XXX.XXX.XXX-XX)
    """
    cpf = re.sub(r'[^0-9]', '', str(cpf))
    if len(cpf) == 11:
        return f'{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}'
    return cpf


def format_cnpj(cnpj: str) -> str:
    """
    Formata CNPJ com pontos, barra e traço.
    
    Args:
        cnpj: CNPJ sem formatação
        
    Returns:
        CNPJ formatado (XX.XXX.XXX/XXXX-XX)
    """
    cnpj = re.sub(r'[^0-9]', '', str(cnpj))
    if len(cnpj) == 14:
        return f'{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}'
    return cnpj


def format_phone(phone: str) -> str:
    """
    Formata telefone brasileiro.
    
    Args:
        phone: Telefone sem formatação
        
    Returns:
        Telefone formatado
    """
    phone = re.sub(r'[^0-9]', '', str(phone))
    if len(phone) == 11:
        return f'({phone[:2]}) {phone[2:7]}-{phone[7:]}'
    elif len(phone) == 10:
        return f'({phone[:2]}) {phone[2:6]}-{phone[6:]}'
    return phone


def format_cep(cep: str) -> str:
    """
    Formata CEP brasileiro.
    
    Args:
        cep: CEP sem formatação
        
    Returns:
        CEP formatado (XXXXX-XXX)
    """
    cep = re.sub(r'[^0-9]', '', str(cep))
    if len(cep) == 8:
        return f'{cep[:5]}-{cep[5:]}'
    return cep


def clean_document(value: str) -> str:
    """
    Remove formatação de documentos (CPF, CNPJ, etc).
    
    Args:
        value: Documento com formatação
        
    Returns:
        Documento apenas com números
    """
    return re.sub(r'[^0-9]', '', str(value))


def calculate_age(birth_date: date) -> int:
    """
    Calcula idade a partir da data de nascimento.
    
    Args:
        birth_date: Data de nascimento
        
    Returns:
        Idade em anos
    """
    today = date.today()
    age = today.year - birth_date.year
    
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    
    return age


def calculate_tenure(admission_date: date, end_date: Optional[date] = None) -> dict:
    """
    Calcula tempo de empresa.
    
    Args:
        admission_date: Data de admissão
        end_date: Data final (default: hoje)
        
    Returns:
        Dict com anos, meses e dias
    """
    if end_date is None:
        end_date = date.today()
    
    years = end_date.year - admission_date.year
    months = end_date.month - admission_date.month
    days = end_date.day - admission_date.day
    
    if days < 0:
        months -= 1
        days += 30
    
    if months < 0:
        years -= 1
        months += 12
    
    return {
        'years': years,
        'months': months,
        'days': days,
        'total_months': years * 12 + months,
        'description': f'{years} anos, {months} meses e {days} dias'
    }


def format_currency(value: Decimal, currency: str = 'BRL') -> str:
    """
    Formata valor monetário.
    
    Args:
        value: Valor a formatar
        currency: Código da moeda
        
    Returns:
        Valor formatado
    """
    if currency == 'BRL':
        return f'R$ {value:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    return f'{currency} {value:,.2f}'


def generate_protocol(prefix: str = '', length: int = 8) -> str:
    """
    Gera número de protocolo único.
    
    Args:
        prefix: Prefixo do protocolo
        length: Tamanho do número
        
    Returns:
        Protocolo gerado
    """
    import uuid
    import time
    
    timestamp = str(int(time.time()))[-4:]
    unique = uuid.uuid4().hex[:length - 4].upper()
    
    if prefix:
        return f'{prefix}-{timestamp}{unique}'
    return f'{timestamp}{unique}'


def mask_cpf(cpf: str) -> str:
    """
    Mascara CPF para exibição (XXX.***.***-XX).
    
    Args:
        cpf: CPF a mascarar
        
    Returns:
        CPF mascarado
    """
    cpf = clean_document(cpf)
    if len(cpf) == 11:
        return f'{cpf[:3]}.***.***.{cpf[9:]}'
    return '***'


def mask_email(email: str) -> str:
    """
    Mascara email para exibição.
    
    Args:
        email: Email a mascarar
        
    Returns:
        Email mascarado
    """
    if '@' not in email:
        return '***'
    
    local, domain = email.split('@')
    if len(local) <= 2:
        masked_local = '*' * len(local)
    else:
        masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
    
    return f'{masked_local}@{domain}'


def slugify_safe(value: str) -> str:
    """
    Gera slug seguro a partir de string.
    
    Args:
        value: String original
        
    Returns:
        Slug gerado
    """
    from django.utils.text import slugify
    return slugify(value, allow_unicode=False)


def hash_value(value: str, algorithm: str = 'sha256') -> str:
    """
    Gera hash de uma string.
    
    Args:
        value: Valor a fazer hash
        algorithm: Algoritmo de hash
        
    Returns:
        Hash gerado
    """
    if algorithm == 'sha256':
        return hashlib.sha256(value.encode()).hexdigest()
    elif algorithm == 'md5':
        return hashlib.md5(value.encode()).hexdigest()
    else:
        raise ValueError(f'Algoritmo não suportado: {algorithm}')


def truncate_string(value: str, length: int = 50, suffix: str = '...') -> str:
    """
    Trunca string com sufixo.
    
    Args:
        value: String a truncar
        length: Tamanho máximo
        suffix: Sufixo a adicionar
        
    Returns:
        String truncada
    """
    if len(value) <= length:
        return value
    return value[:length - len(suffix)] + suffix


def parse_date(value: str) -> Optional[date]:
    """
    Converte string para data.
    
    Args:
        value: String com data
        
    Returns:
        Objeto date ou None
    """
    formats = [
        '%Y-%m-%d',
        '%d/%m/%Y',
        '%d-%m-%Y',
        '%Y/%m/%d',
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    
    return None
