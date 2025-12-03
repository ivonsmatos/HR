#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Traduzir todos os strings em admin.py para PT-BR (VERSÃO COMPLETA)
Traduz fieldsets, short_description e outros labels
"""

import os
import re

# Mapeamento COMPLETO de labels em inglês para português
LABELS_TRANSLATION = {
    # Admin genérico - Fieldsets
    'Basic Information': 'Informações Básicas',
    'Basic Info': 'Informações Básicas',
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
    'Contact': 'Contato',
    'Address': 'Endereço',
    'Organization': 'Organização',
    'Branding': 'Marca',
    'Subscription': 'Assinatura',
    'Domain Info': 'Informações do Domínio',
    'Permissions': 'Permissões',
    'Important Dates': 'Datas Importantes',
    'Groups': 'Grupos',
    'Active': 'Ativo',
    'Superuser': 'Superusuário',
    'Staff': 'Equipe',
    'Company & Profile': 'Empresa & Perfil',
    'HR Details': 'Detalhes de RH',
    'Security': 'Segurança',
    'Preferences': 'Preferências',
    'Activity': 'Atividade',
    
    # Work
    'Project Details': 'Detalhes do Projeto',
    'Assignments': 'Atribuições',
    'Task Details': 'Detalhes da Tarefa',
    'Time Tracking': 'Rastreamento de Tempo',
    'Contract Details': 'Detalhes do Contrato',
    'Allocations': 'Alocações',
    'Comments': 'Comentários',
    'Basic': 'Básico',
    'Dates': 'Datas',
    'Team': 'Equipe',
    
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
    'Work Schedule': 'Agenda de Trabalho',
    'Attendance': 'Presença',
    
    # Finance
    'Invoice Details': 'Detalhes da Fatura',
    'Line Items': 'Itens de Linha',
    'Estimate Details': 'Detalhes da Estimativa',
    'Proposal Details': 'Detalhes da Proposta',
    'Expense Details': 'Detalhes da Despesa',
    'Payment Details': 'Detalhes do Pagamento',
    'Payment Categories': 'Categorias de Pagamento',
    'Transactions': 'Transações',
    'Amounts': 'Valores',
    
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
    'Pipeline': 'Pipeline',
    'Pricing': 'Precificação',
    
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
    'Requirements': 'Requisitos',
    'Position': 'Posição',
    
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
    'Billing': 'Faturamento',
    
    # Utilities
    'Ticket Details': 'Detalhes do Ticket',
    'Ticket Information': 'Informações do Ticket',
    'Asset Details': 'Detalhes do Ativo',
    'Asset Information': 'Informações do Ativo',
    'Event Information': 'Informações do Evento',
    'Message Details': 'Detalhes da Mensagem',
    'Message Information': 'Informações da Mensagem',
    'Knowledge Base': 'Base de Conhecimento',
    'Article Details': 'Detalhes do Artigo',
    'Support': 'Suporte',
    'Internal': 'Interno',
    
    # Atributos comuns
    'Company': 'Empresa',
    'Created': 'Criado',
    'Updated': 'Atualizado',
    'Modified': 'Modificado',
    'Deleted': 'Deletado',
}

# Tradução de short_description
SHORT_DESC_TRANSLATION = {
    'Company': 'Empresa',
    'Title': 'Título',
    'Name': 'Nome',
    'Email': 'Email',
    'Phone': 'Telefone',
    'Status': 'Status',
    'Active': 'Ativo',
    'Created': 'Criado',
    'Updated': 'Atualizado',
    'User': 'Usuário',
    'Date': 'Data',
    'Amount': 'Valor',
    'Type': 'Tipo',
    'Category': 'Categoria',
    'Description': 'Descrição',
    'Notes': 'Observações',
    'Quantity': 'Quantidade',
    'Price': 'Preço',
    'Total': 'Total',
    'Count': 'Contagem',
    'Chunks': 'Fragmentos',
    'Department': 'Departamento',
    'Position': 'Posição',
    'Salary': 'Salário',
    'Hours': 'Horas',
    'Rate': 'Taxa',
    'Level': 'Nível',
    'Rating': 'Classificação',
    'Percentage': 'Porcentagem',
    'Day': 'Dia',
    'Month': 'Mês',
    'Year': 'Ano',
    'Number': 'Número',
    'Code': 'Código',
    'Version': 'Versão',
    'File': 'Arquivo',
    'URL': 'URL',
    'Link': 'Link',
    'Value': 'Valor',
    'State': 'Estado',
    'City': 'Cidade',
    'Country': 'País',
    'Zip': 'CEP',
    'Postal Code': 'Código Postal',
    'Address': 'Endereço',
    'Contact': 'Contato',
    'Industry': 'Indústria',
    'Size': 'Tamanho',
    'Currency': 'Moeda',
    'Timezone': 'Fuso Horário',
    'Language': 'Idioma',
    'Template': 'Modelo',
    'Verified': 'Verificado',
    'Trial': 'Teste',
    'Enabled': 'Ativado',
    'Disabled': 'Desativado',
    'Pending': 'Pendente',
    'Approved': 'Aprovado',
    'Rejected': 'Rejeitado',
    'Submitted': 'Enviado',
    'Completed': 'Concluído',
    'In Progress': 'Em Progresso',
    'Open': 'Aberto',
    'Closed': 'Fechado',
    'Draft': 'Rascunho',
    'Published': 'Publicado',
    'Archived': 'Arquivado',
    'Cancelled': 'Cancelado',
}

def translate_admin_file(filepath):
    """Traduzir um arquivo admin.py"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Traduzir fieldsets
    for en, pt in LABELS_TRANSLATION.items():
        # Pattern para fieldsets: ('English String', {
        pattern = rf"(\(|,\s*)'{re.escape(en)}'(\s*,\s*\{{)"
        replacement = rf"\1'{pt}'\2"
        content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
    
    # Traduzir short_description
    for en, pt in SHORT_DESC_TRANSLATION.items():
        # Pattern para .short_description = 'English String'
        pattern = rf"\.short_description\s*=\s*['\"]({re.escape(en)})['\"]"
        replacement = rf".short_description = '{pt}'"
        content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
    
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
