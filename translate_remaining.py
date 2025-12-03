#!/usr/bin/env python3
"""
Script completo para traduzir TODO o projeto para PT-BR
"""

import os
import re

# Mapeamento completo de traduções
COMPLETE_TRANSLATIONS = {
    # help_text genérico
    '"Company (Tenant) this record belongs to"': '"Empresa (Tenant) a qual este registro pertence"',
    '"Is this the primary domain for the company?"': '"Este é o domínio primário da empresa?"',
    '"Company this user belongs to"': '"Empresa a qual este usuário pertence"',
    
    # Assistant app - Document
    '"Document title (e.g., \'Installation Guide\')"': '"Título do documento (ex: \'Guia de Instalação\')"',
    '"Original file path (e.g., \'docs/setup.md\')"': '"Caminho original do arquivo (ex: \'docs/setup.md\')"',
    '"Full document content"': '"Conteúdo completo do documento"',
    '"Document version"': '"Versão do documento"',
    '"Include in RAG knowledge base"': '"Incluir na base de conhecimento RAG"',
    
    # Assistant app - DocumentChunk
    '"Sequential chunk number within document"': '"Número sequencial do chunk dentro do documento"',
    '"Text content of this chunk"': '"Conteúdo de texto deste chunk"',
    '"OpenAI embedding vector (1536 dimensions for text-embedding-3-small)"': '"Vetor de embedding da OpenAI (1536 dimensões para text-embedding-3-small)"',
    '"Token count for this chunk"': '"Contagem de tokens para este chunk"',
    '"OpenAI model used for embedding"': '"Modelo OpenAI usado para embedding"',
    
    # Assistant app - Conversation
    '"Auto-generated conversation title"': '"Título da conversa gerado automaticamente"',
    '"Mark as archived"': '"Marcar como arquivado"',
    
    # Assistant app - Message
    '"Who sent the message"': '"Quem enviou a mensagem"',
    '"Message content"': '"Conteúdo da mensagem"',
    '"Documents/chunks used for response (RAG context)"': '"Documentos/chunks usados para resposta (contexto RAG)"',
    '"OpenAI tokens consumed by this message"': '"Tokens OpenAI consumidos por esta mensagem"',
    
    # Assistant app - HelixConfig
    '"Enable Helix for this company"': '"Ativar Helix para esta empresa"',
    '"System prompt for LLM (Portuguese)"': '"Prompt de sistema para LLM (Português)"',
    '"Maximum number of document chunks to use as context"': '"Número máximo de chunks de documento para usar como contexto"',
    '"LLM temperature (0.0 to 1.0)"': '"Temperatura do LLM (0,0 a 1,0)"',
    '"Include source citations in responses"': '"Incluir citações de fonte nas respostas"',
    '"Minimum similarity score for relevant chunks (0.0 to 1.0)"': '"Escore mínimo de similaridade para chunks relevantes (0,0 a 1,0)"',
}

def translate_file(file_path):
    """Traduzir um arquivo Python."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Aplicar traduções
        for english, portuguese in COMPLETE_TRANSLATIONS.items():
            content = content.replace(english, portuguese)
        
        # Apenas escrever se algo mudou
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Erro ao processar {file_path}: {e}")
        return False

def main():
    """Traduzir todos os arquivos de modelos."""
    apps_dir = "apps"
    translated_count = 0
    
    for app in os.listdir(apps_dir):
        models_file = os.path.join(apps_dir, app, "models.py")
        if os.path.exists(models_file):
            if translate_file(models_file):
                print(f"✅ Traduzido: {models_file}")
                translated_count += 1
            else:
                print(f"⏭️  Pulado (sem mudanças): {models_file}")
    
    print(f"\n✅ Total de arquivos traduzidos: {translated_count}")

if __name__ == "__main__":
    main()
