# 🚀 HELIX SECRETARY - SETUP OLLAMA (Fase A)

**Stack Local**: Qwen 2.5 14B + Nomic Embeddings + Django + PostgreSQL + pgvector

---

## 📋 Pré-Requisitos

- **Hardware**: 32GB RAM (mínimo 24GB para modelo 14B)
- **Ollama**: Instalado e rodando em `http://localhost:11434`
- **PostgreSQL**: 15+ com extensão `vector` (ativada via migration)
- **Python**: 3.10+
- **Django**: 5.0.1 (projeto SyncRH)

---

## ✅ PASSO 1: Instalar Ollama

### Windows

1. **Download**: https://ollama.ai/download/windows
2. **Instalar**: Execute o instalador
3. **Verificar**:
   ```powershell
   ollama --version
   ```

### macOS

```bash
brew install ollama
```

### Linux

```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

---

## ✅ PASSO 2: Puxar Modelos Requeridos

### Terminal/PowerShell

```bash
# Qwen 2.5 14B (modelo LLM principal)
ollama pull qwen2.5:14b

# Nomic Embed Text (embeddings)
ollama pull nomic-embed-text
```

**Tempo estimado**: 15-30 min (depende da velocidade de internet)  
**Espaço em disco**: ~15GB para ambos os modelos

### Verificar Modelos Instalados

```bash
ollama list
```

**Esperado**:

```
NAME                     ID              SIZE      MODIFIED
qwen2.5:14b             a3c8e0a1b3c4   8.5GB     2 hours ago
nomic-embed-text        f5b2c1d6e9f0   274MB     2 hours ago
```

---

## ✅ PASSO 3: Iniciar Ollama (Background)

### Windows (Automático)

Ollama inicia automaticamente como serviço. Verificar:

```powershell
# Verificar se está rodando
curl http://localhost:11434/api/tags

# Deve retornar JSON com lista de modelos
```

### macOS/Linux (Manual)

```bash
# Terminal 1: Iniciar servidor
ollama serve

# Terminal 2: Verificar
curl http://localhost:11434/api/tags
```

**Resposta esperada**:

```json
{
  "models": [
    {
      "name": "qwen2.5:14b:latest",
      "modified_at": "2024-01-15T10:30:00Z",
      "size": 8500000000,
      "digest": "a3c8e0a1b3c4..."
    },
    {
      "name": "nomic-embed-text:latest",
      "modified_at": "2024-01-15T10:25:00Z",
      "size": 274000000,
      "digest": "f5b2c1d6e9f0..."
    }
  ]
}
```

---

## ✅ PASSO 4: Configurar Django

### 1. Instalar Dependências

```bash
cd c:\Users\ivonm\OneDrive\Documents\GitHub\HR

# Instalar todas as dependências (inclui langchain-ollama)
pip install -r requirements.txt
```

### 2. Configurar `.env`

```bash
# Adicionar ao arquivo .env (se não existir, criar)
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=qwen2.5:14b
EMBEDDING_MODEL=nomic-embed-text
```

### 3. Aplicar Migrations

```bash
python manage.py migrate
```

**Esperado**:

```
Operations to perform:
  Apply all migrations: ...
Running migrations:
  Applying assistant.0001_initial... OK
  (pgvector extension activated)
```

### 4. Testar Conexão

```bash
python manage.py shell

# No Python REPL:
from apps.assistant.services import check_ollama_connection, verify_ollama_models, get_helix_status

# Teste 1: Ollama está rodando?
print(check_ollama_connection())  # Deve ser True

# Teste 2: Modelos disponíveis?
print(verify_ollama_models())
# Expected: {'qwen2.5:14b': True, 'nomic-embed-text': True}

# Teste 3: Status geral
print(get_helix_status())
# Expected: {'ollama_running': True, 'models_available': {...}, 'llm_initialized': True, ...}

# Sair
exit()
```

---

## ✅ PASSO 5: Ingerir Documentos

```bash
python manage.py shell

# No Python REPL:
from apps.assistant.services import DocumentIngestion
from apps.core.models import Company

# Assumir que company_id=1 existe (seu tenant)
# Se não, executar:
# Company.objects.create(id=1, name="Test", slug="test")

result = DocumentIngestion.ingest_documents(company_id=1)
print(result)

# Expected output:
# {
#     'documents_ingested': 5,
#     'chunks_created': 120,
#     'errors': 0,
#     'status': 'success',
#     'message': 'Ingested 5 documents with 120 chunks'
# }

exit()
```

**O que acontece**:

1. Lê todos os `.md`, `.txt`, `.html` de `docs/`
2. Chunking com overlap (1000 tokens, 200 overlap)
3. Gera embeddings via Ollama (nomic-embed-text)
4. Salva DocumentChunk records com vectors em pgvector

---

## ✅ PASSO 6: Testar Chat (CLI)

```bash
python manage.py shell

# No Python REPL:
from apps.assistant.services import HelixAssistant
from apps.core.models import Company
from django.contrib.auth.models import User

# Setup
company = Company.objects.get(id=1)
user = User.objects.first()  # ou criar se não existir

# Criar conversa
from apps.assistant.models import Conversation
conv, _ = Conversation.objects.get_or_create(
    user=user,
    company=company,
    defaults={'title': 'Test Chat'}
)

# Chat!
response = HelixAssistant.chat(
    user_message="O que é o sistema Onyx?",
    conversation=conv,
    user_id=user.id
)

print("Response:")
print(response['response'])
print("\nCitations:")
for citation in response['citations']:
    print(f"  - {citation['title']}")
print(f"\nProcessing time: {response['processing_time']}s")

exit()
```

---

## 🔧 Troubleshooting

### ❌ "Connection refused - Ollama not running"

**Solução**:

```bash
# Verificar se Ollama está rodando
curl http://localhost:11434/api/tags

# Se falhar, iniciar Ollama
ollama serve  # ou use a GUI (Windows)
```

### ❌ "Model not found: qwen2.5:14b"

**Solução**:

```bash
ollama pull qwen2.5:14b
```

### ❌ "Out of memory" / "CUDA out of memory"

**Solução**:

- Modelo 14B precisa de ~16GB de VRAM ou RAM
- Verifique: `ollama list` → tamanho dos modelos
- Se RAM < 24GB, considere modelo menor: `ollama pull qwen2:7b`

### ❌ "pgvector extension not found"

**Solução**:

```bash
python manage.py migrate assistant
# Migration 0001_initial ativa: CREATE EXTENSION vector
```

### ❌ Embeddings lentos

**Nota**: Primeira geração é lenta (~1-5 min para 100 chunks)  
**Próximas**: Muito rápidas (cache)

---

## 📊 Performance Esperada

| Operação                   | Tempo     | Hardware        |
| -------------------------- | --------- | --------------- |
| Pull modelo (14B)          | 10-20 min | Conexão 100Mbps |
| Ingerir 5 docs (50 chunks) | 2-5 min   | Ollama + Nomic  |
| Chat (1 query)             | 5-15 seg  | CPU (no GPU)    |
| Similarity search          | <100ms    | pgvector        |

---

## 🎯 Próximos Passos

1. ✅ Setup Ollama completo
2. 🚀 Fase B: Implementação RAG (services.py)
3. 🎨 Fase C: Interface HTMX (templates)
4. 🔗 Fase D: Integração global (base.html)

---

## 📖 Referências

- **Ollama Docs**: https://github.com/ollama/ollama
- **Qwen Model**: https://huggingface.co/Qwen/Qwen2.5-14B
- **Nomic Embeddings**: https://huggingface.co/nomic-ai/nomic-embed-text-v1
- **LangChain + Ollama**: https://python.langchain.com/docs/integrations/llms/ollama
- **pgvector**: https://github.com/pgvector/pgvector

---

**✅ Setup Completo!**  
Você tem agora um sistema RAG 100% local rodando em sua máquina. 🎉
