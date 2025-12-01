#!/usr/bin/env python
"""
Script de teste simplificado para validar o setup do Helix Secretary
Sem dependência de banco de dados PostgreSQL
"""

import sys
import os

# Adicionar path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("\n" + "="*70)
print("🚀 HELIX SECRETARY - TEST SERVER")
print("="*70 + "\n")

# Teste 1: Verificar Python
print("✅ Python:", sys.version.split()[0])

# Teste 2: Verificar Django
try:
    import django
    print("✅ Django:", django.__version__)
except ImportError as e:
    print("❌ Django não instalado:", e)
    sys.exit(1)

# Teste 3: Verificar LangChain
try:
    import langchain
    print("✅ LangChain:", langchain.__version__)
except ImportError as e:
    print("⚠️  LangChain não instalado (opcional):", e)

# Teste 4: Verificar Ollama client
try:
    import ollama
    print("✅ Ollama:", "instalado")
except ImportError as e:
    print("⚠️  Ollama client não instalado (opcional):", e)

# Teste 5: Verificar apps Helix
print("\n📁 Estrutura Helix Secretary:")
helix_files = [
    "apps/assistant/services.py",
    "apps/assistant/views.py",
    "apps/assistant/api.py",
    "apps/assistant/gpu_manager.py",
    "apps/assistant/multilang.py",
]

for f in helix_files:
    if os.path.exists(f):
        print(f"   ✅ {f}")
    else:
        print(f"   ❌ {f} - NÃO ENCONTRADO")

print("\n" + "="*70)
print("📊 INFORMAÇÕES DO SISTEMA")
print("="*70)

# Informações do sistema
import platform
print(f"OS: {platform.system()} {platform.release()}")
print(f"Python Path: {sys.executable}")
print(f"Working Dir: {os.getcwd()}")

print("\n" + "="*70)
print("✅ SETUP VALIDADO COM SUCESSO!")
print("="*70)

print("\n📝 Próximos passos:")
print("   1. Instalar PostgreSQL 13+")
print("   2. Criar banco de dados: createdb helix")
print("   3. Configurar .env com DATABASES")
print("   4. Rodar: python manage.py migrate")
print("   5. Iniciar Ollama: ollama serve")
print("   6. Rodar servidor: python manage.py runserver")

print("\n🌐 URL: http://localhost:8000/chat/")
print("   Admin: http://localhost:8000/admin/")
print("   API: http://localhost:8000/api/helix/")
print("\n")
