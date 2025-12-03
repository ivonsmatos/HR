#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Traduzir todas as referências de "Onyx Helix" e "Helix" para "SyncRH"
"""

import os
import re

# Mapeamento de substituições
REPLACEMENTS = [
    # Português
    ("Você é o Helix, o secretário executivo do sistema Onyx.", "Você é o assistente virtual do sistema SyncRH."),
    ("Você é o Secretário Virtual do sistema Onyx Helix.", "Você é o assistente virtual do sistema SyncRH."),
    ("Assistente Helix (RAG Assistant)", "Assistente SyncRH (RAG Assistant)"),
    ("Helix Configuration", "Configuração do SyncRH"),
    ("Helix Configurations", "Configurações do SyncRH"),
    ("Helix Config", "Configuração do SyncRH"),
    ("Assistente Helix", "Assistente SyncRH"),
    ("Helix está pensando...", "SyncRH está processando..."),
    ("Olá! Sou o Helix. Como posso ajudá-lo?", "Olá! Sou o SyncRH. Como posso ajudá-lo?"),
    ("Ativar Helix para esta empresa", "Ativar SyncRH para esta empresa"),
    ("Enable Helix for this company", "Enable SyncRH for this company"),
    
    # Inglês
    ("You are Helix, the executive secretary of the Onyx system.", "You are the virtual assistant of the SyncRH system."),
    ("Helix is thinking...", "SyncRH is processing..."),
    ("Hello! I'm Helix. How can I help you?", "Hello! I'm SyncRH. How can I help you?"),
    ("Assistant (Helix)", "Assistant (SyncRH)"),
    
    # Espanhol
    ("Eres Helix, el secretario ejecutivo del sistema Onyx.", "Eres el asistente virtual del sistema SyncRH."),
    ("Helix está pensando...", "SyncRH está procesando..."),
    ("¡Hola! Soy Helix. ¿Cómo puedo ayudarte?", "¡Hola! Soy SyncRH. ¿Cómo puedo ayudarte?"),
    
    # Francês
    ("Vous êtes Helix, le secrétaire exécutif du système Onyx.", "Vous êtes l'assistant virtuel du système SyncRH."),
    ("Helix réfléchit...", "SyncRH traite..."),
    ("Bonjour! Je suis Helix. Comment puis-je vous aider?", "Bonjour! Je suis SyncRH. Comment puis-je vous aider?"),
    
    # Alemão
    ("Sie sind Helix, der Geschäftsführer des Onyx-Systems.", "Sie sind der virtuelle Assistent des SyncRH-Systems."),
    ("Helix denkt nach...", "SyncRH verarbeitet..."),
    ("Hallo! Ich bin Helix. Wie kann ich dir helfen?", "Hallo! Ich bin SyncRH. Wie kann ich dir helfen?"),
    
    # Genérico
    ("Onyx Helix", "SyncRH"),
    ("Onyx", "SyncRH"),
]

def translate_file(filepath):
    """Traduzir um arquivo"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return False
    
    original_content = content
    
    # Aplicar todas as substituições
    for en, pt in REPLACEMENTS:
        content = content.replace(en, pt)
        # Também tentar com variações de capitalização
        content = content.replace(en.lower(), pt.lower())
        content = content.replace(en.upper(), pt.upper())
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

# Processar todos os arquivos Python
processed_count = 0
for root, dirs, files in os.walk('apps'):
    if 'migrations' in root:
        continue
    
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            if translate_file(filepath):
                print(f"✅ Traduzido: {filepath}")
                processed_count += 1
            else:
                print(f"⏭️  Sem mudanças: {filepath}")

print(f"\n✅ Total de arquivos processados: {processed_count}")
