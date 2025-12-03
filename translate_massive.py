#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tradução COMPLETA - Varrer todos os arquivos e traduzir 100% para PT-BR
"""

import os
import re

# Dicionário MASSIVO de traduções
MASSIVE_TRANSLATION = {
    # Assistente Helix
    "Assistente Helix (RAG Assistant)": "Assistente SyncRH (Assistente RAG)",
    "ASSISTENTE HELIX (RAG ASSISTANT)": "ASSISTENTE SYNCRH (ASSISTENTE RAG)",
    "Assistente Helix": "Assistente SyncRH",
    "ASSISTENTE HELIX": "ASSISTENTE SYNCRH",
    
    # Textos comuns em inglês
    "Who sent the message": "Quem enviou a mensagem",
    "Message content": "Conteúdo da mensagem",
    "Documents/chunks used for response context": "Documentos/chunks usados para contexto de resposta",
    "Auto-generated conversation title": "Título da conversa gerado automaticamente",
    "Mark as archived": "Marcar como arquivado",
    "Company (Tenant) this record belongs to": "Empresa (Tenant) à qual este registro pertence",
    "Is active": "Está ativo",
    "Is enabled": "Está ativado",
    "Enable SyncRH for this company": "Ativar SyncRH para esta empresa",
    "System prompt for LLM (Portuguese)": "Prompt do sistema para LLM (Português)",
    "Maximum context chunks to use": "Máximo de chunks de contexto para usar",
    "Minimum similarity score for relevant chunks": "Escore mínimo de similaridade para chunks relevantes",
    "LLM temperature (0.0 to 1.0)": "Temperatura do LLM (0,0 a 1,0)",
    "Include citations in responses": "Incluir citações nas respostas",
    
    # Fields
    "Title": "Título",
    "Source path": "Caminho de origem",
    "Content type": "Tipo de conteúdo",
    "Version": "Versão",
    "Ingested at": "Ingerido em",
    "Updated at": "Atualizado em",
    "Created at": "Criado em",
    "Chunk index": "Índice do chunk",
    "Content": "Conteúdo",
    "Embedding": "Incorporação",
    "Token count": "Contagem de tokens",
    "Embedding model": "Modelo de incorporação",
    "User": "Usuário",
    "Company": "Empresa",
    "Role": "Papel",
    "Tokens used": "Tokens usados",
    "Context sources": "Fontes de contexto",
    "Is active": "Está ativo",
    "Temperature": "Temperatura",
    "Max context chunks": "Máximo de chunks de contexto",
    "Similarity threshold": "Limite de similaridade",
    
    # Sections/Categories
    "Message Info": "Informações da Mensagem",
    "Content": "Conteúdo",
    "Metadata": "Metadados",
    "Audit": "Auditoria",
    "Document Reference": "Referência do Documento",
    "Embedding": "Incorporação",
    "Conversation Info": "Informações da Conversa",
    "Status": "Status",
    "System Prompt": "Prompt do Sistema",
    "Response Settings": "Configurações de Resposta",
    "Features": "Recursos",
    "Configuration": "Configuração",
    "Basic Information": "Informações Básicas",
    
    # Help texts
    "Title of the document": "Título do documento",
    "Original file path": "Caminho do arquivo original",
    "Full document content": "Conteúdo completo do documento",
    "Document version": "Versão do documento",
    "Include in RAG knowledge base": "Incluir na base de conhecimento RAG",
    "Sequential chunk number within document": "Número sequencial do chunk dentro do documento",
    "Content of this chunk": "Conteúdo deste chunk",
    "OpenAI embedding vector (1536 dimensions for text-embedding-3-small)": "Vetor de incorporação da OpenAI (1536 dimensões para text-embedding-3-small)",
    "Token count for this chunk": "Contagem de tokens para este chunk",
    "OpenAI model used for embedding": "Modelo OpenAI usado para incorporação",
    
    # Common UI
    "Add": "Adicionar",
    "Save": "Salvar",
    "Delete": "Deletar",
    "Edit": "Editar",
    "Change": "Alterar",
    "Search": "Pesquisar",
    "Filter": "Filtrar",
    "Sort": "Ordenar",
    "Export": "Exportar",
    "Import": "Importar",
    "Close": "Fechar",
    "Cancel": "Cancelar",
    "Continue": "Continuar",
    "Next": "Próximo",
    "Previous": "Anterior",
    "Back": "Voltar",
    "Home": "Início",
    "Dashboard": "Painel",
    "Settings": "Configurações",
    "Profile": "Perfil",
    "Logout": "Sair",
    "Login": "Entrar",
    "Password": "Senha",
    "Email": "Email",
    "Name": "Nome",
    "Yes": "Sim",
    "No": "Não",
    "OK": "OK",
    "Error": "Erro",
    "Success": "Sucesso",
    "Warning": "Aviso",
    "Info": "Informação",
    
    # Messages
    "Hello! I'm SyncRH. How can I help you?": "Olá! Sou o SyncRH. Como posso ajudá-lo?",
    "SyncRH is thinking...": "SyncRH está processando...",
    "No results found": "Nenhum resultado encontrado",
    "An error occurred": "Ocorreu um erro",
    "Please try again": "Por favor, tente novamente",
    "Loading...": "Carregando...",
    "Processing...": "Processando...",
    
    # Django admin
    "administration": "administração",
    "Add": "Adicionar",
    "Change": "Alterar",
    "Delete": "Deletar",
    "View on site": "Ver no site",
    "History": "Histórico",
    "Recent actions": "Ações recentes",
    
    # Sections em admin (sidebar)
    "Conversations": "Conversas",
    "Document Chunks": "Fragmentos de Documentos",
    "Documents": "Documentos",
    "Helix Configurations": "Configurações do SyncRH",
    "Messages": "Mensagens",
    "Subscriptions": "Assinaturas",
    "Discount Codes": "Códigos de Desconto",
    "Invoices": "Faturas",
    "Plans": "Planos",
    "Audit Logs": "Logs de Auditoria",
    "Company Domains": "Domínios da Empresa",
    "Empresas": "Empresas",
    "User Permissions": "Permissões do Usuário",
    "Users": "Usuários",
    "Groups": "Grupos",
    "Departments": "Departamentos",
    "Designations": "Designações",
    "Employees": "Funcionários",
    "Leave Types": "Tipos de Licença",
    "Leaves": "Licenças",
    "Shifts": "Turnos",
    "Attendance": "Presença",
    "Salary Structures": "Estruturas Salariais",
    "Employee Salaries": "Salários dos Funcionários",
    "Payslips": "Contracheques",
    "Performance Goals": "Objetivos de Desempenho",
    "Performance Reviews": "Avaliações de Desempenho",
    
    # Documentação/Comments
    "Stores conversation history": "Armazena histórico de conversa",
    "Individual message in a conversation": "Mensagem individual em uma conversa",
    "Represents a document ingested for RAG": "Representa um documento ingerido para RAG",
    "Stores metadata about source files and chunks": "Armazena metadados sobre arquivos de origem e chunks",
    "Document chunk with embeddings": "Chunk de documento com incorporações",
    "Stores embedding vectors for similarity search": "Armazena vetores de incorporação para busca de similaridade",
    "Conversation with RAG Assistant": "Conversa com o Assistente RAG",
    "Configuration per tenant for SyncRH": "Configuração por tenant para SyncRH",
    
    # Modelos verboses
    "Document": "Documento",
    "Documents": "Documentos",
    "Document Chunk": "Fragmento de Documento",
    "Document Chunks": "Fragmentos de Documentos",
    "Conversation": "Conversa",
    "Conversations": "Conversas",
    "Message": "Mensagem",
    "Messages": "Mensagens",
    "Helix Configuration": "Configuração do SyncRH",
    "Helix Configurations": "Configurações do SyncRH",
}

def traduzir_arquivo(filepath):
    """Traduzir um arquivo"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return False
    
    original = content
    
    # Aplicar substituições em ordem de comprimento (maior primeiro para evitar conflitos)
    items = sorted(MASSIVE_TRANSLATION.items(), key=lambda x: len(x[0]), reverse=True)
    
    for en, pt in items:
        if en != pt:  # Não fazer if iguais
            content = content.replace(en, pt)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

# Listar todos os arquivos Python
print("Varrendo projeto...")
processed = 0
for root, dirs, files in os.walk('apps'):
    # Ignorar migrations e __pycache__
    if 'migrations' in root or '__pycache__' in root:
        continue
    
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            if traduzir_arquivo(filepath):
                print(f"✅ {filepath}")
                processed += 1

print(f"\n✅ Total de arquivos traduzidos: {processed}")
print(f"📊 Total de substituições: {len(MASSIVE_TRANSLATION)}")
