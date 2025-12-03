#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Traduzir todos os choices em models.py para PT-BR
"""

import os
import re

# Mapeamento de status/choices para português
CHOICES_TRANSLATION = {
    # Status geral
    "active": "Ativo",
    "inactive": "Inativo",
    "pending": "Pendente",
    "approved": "Aprovado",
    "rejected": "Rejeitado",
    "draft": "Rascunho",
    "published": "Publicado",
    "archived": "Arquivado",
    "deleted": "Deletado",
    "cancelled": "Cancelado",
    "completed": "Concluído",
    
    # Projetos
    "planning": "Planejamento",
    "paused": "Pausado",
    
    # Contrato
    "signed": "Assinado",
    
    # Tarefas
    "todo": "A Fazer",
    "in_progress": "Em Progresso",
    "blocked": "Bloqueado",
    "on_hold": "Em Espera",
    "in_review": "Em Revisão",
    "done": "Concluído",
    
    # Recrutamento
    "open": "Aberto",
    "closed": "Fechado",
    "new": "Novo",
    "screening": "Triagem",
    "interview": "Entrevista",
    "offer": "Oferta",
    "hired": "Contratado",
    "not_selected": "Não Selecionado",
    "phone": "Telefone",
    "video": "Vídeo",
    "on_site": "Presencial",
    
    # HR/RH
    "active": "Ativo",
    "inactive": "Inativo",
    "on_leave": "De Licença",
    "resigned": "Demitido",
    "sick_leave": "Licença Médica",
    "vacation": "Férias",
    "unpaid": "Sem Remuneração",
    "maternity": "Maternidade",
    "paternity": "Paternidade",
    
    # Finance
    "sent": "Enviado",
    "paid": "Pago",
    "overdue": "Vencido",
    "partial": "Parcial",
    "refunded": "Reembolsado",
    "quote": "Cotação",
    "proposal": "Proposta",
    "estimate": "Estimativa",
    "invoice": "Fatura",
    
    # CRM
    "lead": "Lead",
    "customer": "Cliente",
    "prospect": "Perspectiva",
    "contact": "Contato",
    "qualified": "Qualificado",
    "unqualified": "Desqualificado",
    "converted": "Convertido",
    "lost": "Perdido",
    "qualified_lead": "Lead Qualificado",
    "sales_qualified": "Qualificado para Venda",
    "negotiation": "Negociação",
    "closing": "Fechamento",
    "won": "Ganho",
    
    # SaaS
    "trial": "Teste",
    "free": "Gratuito",
    "pro": "Profissional",
    "enterprise": "Empresarial",
    "monthly": "Mensal",
    "annual": "Anual",
    "expired": "Expirado",
    
    # Utilidades
    "open": "Aberto",
    "in_progress": "Em Progresso",
    "resolved": "Resolvido",
    "closed": "Fechado",
    "low": "Baixo",
    "medium": "Médio",
    "high": "Alto",
    "critical": "Crítico",
    "urgent": "Urgente",
    "important": "Importante",
    "normal": "Normal",
    "working": "Funcionando",
    "maintenance": "Manutenção",
    "broken": "Quebrado",
    "retired": "Aposentado",
    "available": "Disponível",
    "in_use": "Em Uso",
    "reserved": "Reservado",
    
    # Security
    "login": "Login",
    "logout": "Logout",
    "failed_login": "Falha no Login",
    "permission_change": "Mudança de Permissão",
    "data_access": "Acesso a Dados",
    "data_change": "Mudança de Dados",
    "data_delete": "Exclusão de Dados",
    "spam": "SPAM",
    "ddos": "DDoS",
    "suspicious": "Suspeito",
    "verified": "Verificado",
    "blocked": "Bloqueado",
    "temporary": "Temporário",
    "permanent": "Permanente",
    "android": "Android",
    "ios": "iOS",
    "web": "Web",
    "desktop": "Desktop",
    
    # Conhecimento
    "draft": "Rascunho",
    "published": "Publicado",
    "archived": "Arquivado",
    "faq": "FAQ",
    "tutorial": "Tutorial",
    "guide": "Guia",
    "bug_report": "Relatório de Bug",
    "feature_request": "Solicitação de Recurso",
    "documentation": "Documentação",
}

def translate_choices_in_file(filepath):
    """Traduzir choices em um arquivo models.py"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Padrão para encontrar choices
    # ("key", "English Text") -> ("key", "Português")
    for en_key, pt_text in CHOICES_TRANSLATION.items():
        # Procurar por ("key", "Key") ou ("key", "English Phrase")
        # Primeiro tenta encontrar o padrão exato com maiúscula
        key_capitalized = en_key.replace("_", " ").title()
        pattern = rf'(\(\s*["\']' + re.escape(en_key) + r'["\'],\s*["\'])' + re.escape(key_capitalized) + r'(["\'])'
        replacement = rf'\1{pt_text}\2'
        content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

# Processar todos os models.py
model_files = []
for root, dirs, files in os.walk('apps'):
    if 'migrations' not in root:  # Ignorar migrations
        for file in files:
            if file == 'models.py':
                model_files.append(os.path.join(root, file))

print(f"Encontrados {len(model_files)} arquivos models.py\n")

translated_count = 0
for model_file in model_files:
    if translate_choices_in_file(model_file):
        print(f"✅ Traduzido: {model_file}")
        translated_count += 1
    else:
        print(f"⏭️  Sem mudanças: {model_file}")

print(f"\n✅ Total de arquivos traduzidos: {translated_count}")
