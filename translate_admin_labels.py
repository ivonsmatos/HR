#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Traduzir todos os fieldsets e labels em admin.py para PT-BR
"""

import os
import re

# Mapeamento de labels em inglês para português
LABELS_TRANSLATION = {
    # Admin genérico
    'Basic Information': 'Informações Básicas',
    'Content': 'Conteúdo',
    'Metadata': 'Metadados',
    'Audit': 'Auditoria',
    'Document Reference': 'Referência do Documento',
    'Embedding': 'Incorporação',
    'Conversation Info': 'Informações da Conversa',
    'Status': 'Status',
    'Message Info': 'Informações da Mensagem',
    'Document Management': 'Gestão de Documentos',
    'Configuration': 'Configuração',
    'System Monitoring': 'Monitoramento do Sistema',
    
    # Core
    'Personal Information': 'Informações Pessoais',
    'Account': 'Conta',
    'Permissions': 'Permissões',
    'Important Dates': 'Datas Importantes',
    'Groups': 'Grupos',
    'Active': 'Ativo',
    'Superuser': 'Superusuário',
    'Staff': 'Equipe',
    
    # Work
    'Project Details': 'Detalhes do Projeto',
    'Assignments': 'Atribuições',
    'Task Details': 'Detalhes da Tarefa',
    'Time Tracking': 'Rastreamento de Tempo',
    'Contract Details': 'Detalhes do Contrato',
    'Allocations': 'Alocações',
    'Comments': 'Comentários',
    
    # HRM
    'Employee Information': 'Informações do Funcionário',
    'Employment': 'Emprego',
    'Compensation': 'Compensação',
    'Performance': 'Desempenho',
    'Review Information': 'Informações da Revisão',
    'Leave Details': 'Detalhes de Licença',
    'Salary Structure': 'Estrutura Salarial',
    'Payroll': 'Folha de Pagamento',
    'Department Management': 'Gestão de Departamento',
    'Job Position Management': 'Gestão de Posição de Trabalho',
    'Goals': 'Objetivos',
    'Reviews': 'Avaliações',
    
    # Finance
    'Invoice Details': 'Detalhes da Fatura',
    'Line Items': 'Itens de Linha',
    'Estimate Details': 'Detalhes da Estimativa',
    'Proposal Details': 'Detalhes da Proposta',
    'Expense Details': 'Detalhes da Despesa',
    'Payment Details': 'Detalhes do Pagamento',
    'Payment Categories': 'Categorias de Pagamento',
    'Transactions': 'Transações',
    
    # CRM
    'Account Details': 'Detalhes da Conta',
    'Contact Information': 'Informações de Contato',
    'Lead Details': 'Detalhes do Lead',
    'Lead Information': 'Informações do Lead',
    'Product Details': 'Detalhes do Produto',
    'Order Details': 'Detalhes do Pedido',
    'Order Information': 'Informações do Pedido',
    'Product Information': 'Informações do Produto',
    'Stock': 'Estoque',
    'Order Items': 'Itens do Pedido',
    'Sales': 'Vendas',
    
    # Recruitment
    'Job Details': 'Detalhes da Vaga',
    'Position Details': 'Detalhes da Posição',
    'Application Details': 'Detalhes da Aplicação',
    'Candidate Details': 'Detalhes do Candidato',
    'Candidate Information': 'Informações do Candidato',
    'Interview Details': 'Detalhes da Entrevista',
    'Offer Details': 'Detalhes da Oferta',
    'Offer Information': 'Informações da Oferta',
    'Candidate Pool': 'Base de Candidatos',
    
    # Security
    'IP Management': 'Gestão de IP',
    'Blocking Details': 'Detalhes de Bloqueio',
    'User Sessions': 'Sessões de Usuário',
    'Device Management': 'Gestão de Dispositivo',
    'Audit Log': 'Log de Auditoria',
    'Event Details': 'Detalhes do Evento',
    'Security Settings': 'Configurações de Segurança',
    '2FA Settings': 'Configurações de 2FA',
    
    # SaaS
    'Plan Details': 'Detalhes do Plano',
    'Subscription Details': 'Detalhes da Assinatura',
    'Subscription Information': 'Informações da Assinatura',
    'Invoice Information': 'Informações da Fatura',
    'Discount Details': 'Detalhes do Desconto',
    'Discount Information': 'Informações do Desconto',
    'Plans': 'Planos',
    'Subscriptions': 'Assinaturas',
    'Invoices': 'Faturas',
    'Discount Codes': 'Códigos de Desconto',
    
    # Utilities
    'Ticket Details': 'Detalhes do Ticket',
    'Ticket Information': 'Informações do Ticket',
    'Asset Details': 'Detalhes do Ativo',
    'Asset Information': 'Informações do Ativo',
    'Event Details': 'Detalhes do Evento',
    'Event Information': 'Informações do Evento',
    'Message Details': 'Detalhes da Mensagem',
    'Message Information': 'Informações da Mensagem',
    'Knowledge Base': 'Base de Conhecimento',
    'Article Details': 'Detalhes do Artigo',
}

def translate_admin_file(filepath):
    """Traduzir um arquivo admin.py"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Traduzir fieldsets
    for en, pt in LABELS_TRANSLATION.items():
        # Pattern para fieldsets: ('English String', {
        pattern = rf"(\(|,\s*)'{en}'(\s*,\s*\{{)"
        replacement = rf"\1'{pt}'\2"
        content = re.sub(pattern, replacement, content)
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

# Processar todos os admin.py
admin_files = []
for root, dirs, files in os.walk('apps'):
    for file in files:
        if file == 'admin.py':
            admin_files.append(os.path.join(root, file))

print(f"Encontrados {len(admin_files)} arquivos admin.py\n")

translated_count = 0
for admin_file in admin_files:
    if translate_admin_file(admin_file):
        print(f"✅ Traduzido: {admin_file}")
        translated_count += 1
    else:
        print(f"⏭️  Sem mudanças: {admin_file}")

print(f"\n✅ Total de arquivos traduzidos: {translated_count}")
