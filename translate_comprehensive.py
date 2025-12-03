#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script completo para traduzir 100% do projeto para PT-BR e mudar Helix para SyncRH
"""

import os
import re

# Dicionário COMPLETO de traduções
TRANSLATIONS = {
    # Admin.py - docstrings
    "Helix Admin Dashboard - Advanced Admin Interface": "Painel de Administração do SyncRH - Interface Avançada",
    "Custom admin site for Helix": "Site de administração personalizado para SyncRH",
    "Helix Admin": "Admin SyncRH",
    
    # Site titles
    "site_title = \"Helix Admin\"": "site_title = \"Admin SyncRH\"",
    "index_title = \"Dashboard\"": "index_title = \"Painel\"",
    
    # Messages
    "'Assistente Helix - Admin'": "'Painel SyncRH - Administração'",
    "\"Assistente Helix - Admin\"": "\"Painel SyncRH - Administração\"",
    
    # Models
    "class Meta:": "class Meta:",  # Não traduzir
    "Document Chunk": "Fragmento de Documento",
    "Document Chunks": "Fragmentos de Documentos",
    "Conversation": "Conversa",
    "Conversations": "Conversas",
    
    # Help texts em inglês
    "Individual message in a conversation": "Mensagem individual em uma conversa",
    "Enable Helix for this company": "Ativar SyncRH para esta empresa",
    "System prompt for LLM": "Prompt do sistema para o LLM",
    "Temperature of the LLM": "Temperatura do LLM",
    "Maximum context chunks": "Máximo de chunks de contexto",
    "Who sent the message": "Quem enviou a mensagem",
    "Storing conversation history": "Armazenando histórico de conversa",
    
    # Admin list displays
    "Company (Tenant) this record belongs to": "Empresa (Tenant) à qual este registro pertence",
    "Is enabled": "Está ativado",
    "Enable": "Ativar",
    
    # Messages em inglês
    "Hello! I'm Helix. How can I help you?": "Olá! Sou o SyncRH. Como posso ajudá-lo?",
    "I'm Helix": "Sou o SyncRH",
    "I am Helix": "Sou o SyncRH",
    "I'm SyncRH": "Sou o SyncRH",
    
    # Multilang
    "No results found for your search.": "Nenhum resultado encontrado para sua busca.",
    "An error occurred while processing your request.": "Ocorreu um erro ao processar sua solicitação.",
    "An error occurred": "Ocorreu um erro",
    
    # Services
    "Helix configuration": "Configuração do SyncRH",
    "Configuration per tenant": "Configuração por tenant",
    
    # Admin methods
    "Company (Tenant)": "Empresa (Tenant)",
    "LLM temperature": "Temperatura do LLM",
    "Model configuration": "Configuração do modelo",
    "User stats": "Estatísticas de usuário",
}

def replace_all(content, old, new):
    """Replace all occurrences case-insensitive but preserve case"""
    return content.replace(old, new)

def translate_file(filepath):
    """Traduzir arquivo"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return False
    
    original = content
    
    # Aplicar todas as substituições
    for old, new in TRANSLATIONS.items():
        if old != new:  # Não fazer replace se for igual
            content = replace_all(content, old, new)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

# Processar arquivos específicos
files_to_process = [
    'apps/assistant/admin.py',
    'apps/assistant/models.py',
    'apps/assistant/multilang.py',
    'apps/assistant/services.py',
    'apps/assistant/views.py',
    'apps/assistant/api.py',
    'apps/assistant/context_processors.py',
    'apps/assistant/gpu_manager.py',
]

print("Traduzindo arquivos...")
translated = 0
for filepath in files_to_process:
    if os.path.exists(filepath):
        if translate_file(filepath):
            print(f"✅ {filepath}")
            translated += 1
        else:
            print(f"⏭️  {filepath} (sem mudanças)")
    else:
        print(f"❌ {filepath} (não encontrado)")

print(f"\n✅ Total traduzido: {translated} arquivos")
