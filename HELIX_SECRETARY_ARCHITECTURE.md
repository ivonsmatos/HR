# 🏗️ HELIX SECRETARY - ESTRUTURA CRIADA

## Árvore de Arquivos - Fase A

```
HR/
├── apps/
│   └── assistant/                           ← NOVO: Django App para RAG
│       ├── __init__.py                      (15 linhas) - Package init
│       ├── apps.py                          (25 linhas) - AppConfig
│       ├── models.py                        (270 linhas) ⭐ COM PGVECTOR
│       │   ├── Document (TenantAware)       - Docs ingested
│       │   ├── DocumentChunk ⭐             - Vector embeddings (1536 dims)
│       │   ├── Conversation (TenantAware)   - Chat sessions
│       │   ├── Message                      - Chat history
│       │   └── HelixConfig (TenantAware)    - Config per tenant
│       │
│       ├── admin.py                         (140 linhas) - Admin interface
│       │   ├── DocumentAdmin
│       │   ├── DocumentChunkAdmin
│       │   ├── ConversationAdmin
│       │   ├── MessageAdmin
│       │   └── HelixConfigAdmin
│       │
│       ├── views.py                         (150 linhas) - API stubs
│       │   ├── chat_interface()             - GET /chat/
│       │   ├── chat_window()                - GET /chat/window/
│       │   ├── chat_message()               - POST /api/chat/message/
│       │   ├── get_conversation_history()   - GET /api/chat/history/<id>/
│       │   ├── create_conversation()        - POST /api/chat/new/
│       │   ├── list_documents()             - GET /api/documents/
│       │   └── ingest_documents()           - POST /api/documents/ingest/
│       │
│       ├── services.py                      (340 linhas) - RAG skeleton
│       │   ├── DocumentIngestion            - Ingestão de docs
│       │   ├── RAGPipeline                  - Busca de contexto
│       │   └── HelixAssistant               - Chat interface
│       │
│       ├── urls.py                          (20 linhas) - URL routing
│       │   ├── /api/chat/message/
│       │   ├── /api/chat/history/
│       │   ├── /api/chat/new/
│       │   ├── /api/documents/
│       │   ├── /api/documents/ingest/
│       │   ├── /chat/
│       │   └── /chat/window/
│       │
│       └── migrations/
│           ├── __init__.py
│           └── 0001_initial.py              (200+ linhas)
│               ├── CREATE EXTENSION pgvector
│               ├── CREATE TABLE document
│               ├── CREATE TABLE documentchunk
│               ├── CREATE TABLE conversation
│               ├── CREATE TABLE message
│               ├── CREATE TABLE helixconfig
│               └── CREATE INDEXES
│
├── config/
│   └── settings.py                          (MODIFICADO)
│       └── LOCAL_APPS += 'apps.assistant'   ← Adicionado
│
├── requirements.txt                         (MODIFICADO)
│       ├── pgvector==0.2.4                  ← Novo
│       ├── langchain==0.1.4                 ← Novo
│       ├── langchain-openai==0.0.5          ← Novo
│       ├── langchain-postgres==0.0.9        ← Novo
│       └── openai==1.3.8                    ← Novo
│
├── docs/
│   └── manual.md                            ← Adicionado (exemplo doc para ingest)
│
└── Documentation/
    ├── HELIX_SECRETARY_FASE_A_SUMMARY.md         ← Novo
    ├── HELIX_SECRETARY_FASE_B_PLANNING.md        ← Novo
    ├── HELIX_SECRETARY_READY_FOR_FASE_B.md       ← Novo
    ├── HELIX_SECRETARY_STATUS.md                 ← Novo
    └── HELIX_SECRETARY_FASE_A_COMPLETE.txt       ← Novo (visual)
```

---

## 📊 Estatísticas

### Arquivos Criados/Modificados

| Tipo | Qtd | Linhas | Status |
|------|-----|--------|--------|
| **App Files** | 8 | 1,160 | ✅ |
| **Migrations** | 1 | 200+ | ✅ |
| **Config** | 1 | (+1) | ✅ |
| **Dependencies** | 1 | (+5) | ✅ |
| **Documentation** | 5 | 2,000+ | ✅ |
| **TOTAL** | **17** | **~3,400** | ✅ |

### Modelos Django

| Modelo | Campos | Índices | Status |
|--------|--------|---------|--------|
| **Document** | 9 | 2 | ✅ |
| **DocumentChunk** | 8 | 1 | ✅ |
| **Conversation** | 6 | 1 | ✅ |
| **Message** | 7 | 2 | ✅ |
| **HelixConfig** | 7 | 1 | ✅ |

### API Endpoints

| Método | Endpoint | Status |
|--------|----------|--------|
| **GET** | `/chat/` | Stub ⏳ |
| **GET** | `/chat/window/` | Stub ⏳ |
| **POST** | `/api/chat/message/` | Stub ⏳ |
| **GET** | `/api/chat/history/<id>/` | Stub ⏳ |
| **POST** | `/api/chat/new/` | Stub ⏳ |
| **GET** | `/api/documents/` | Stub ⏳ |
| **POST** | `/api/documents/ingest/` | Stub ⏳ |

---

## 🔗 Relacionamentos de Modelos

```
Document (1) ────────────── (N) DocumentChunk
   │                              │
   └─ company (FK)    ├─ embedding (1536 dims)
   ├─ title           └─ document (FK)
   ├─ source_path
   ├─ content
   └─ ingested_at

Company ────┬──────── Document
            │
            ├──────── Conversation
            │
            └──────── HelixConfig

Conversation (1) ────────────── (N) Message
   │                                │
   ├─ user (FK)           └─ role (user|assistant|system)
   ├─ company (FK)        ├─ content
   └─ title               └─ context_sources (JSON)

User ────────────── (N) Conversation
```

---

## 🎯 RAG Classes (services.py)

```python
DocumentIngestion
├── discover_documents()      # Encontrar arquivos
├── parse_document()          # Ler e detectar tipo
├── chunk_text()              # Dividir em chunks
├── generate_embeddings()     # OpenAI embeddings (ASYNC)
└── ingest_documents()        # Pipeline completo

RAGPipeline
├── retrieve_context()        # pgvector similarity search
├── build_prompt()            # Formatar prompt com contexto
└── answer_query()            # Query → Response (ASYNC)

HelixAssistant
├── get_config()              # Get tenant config
├── chat()                    # Full conversation flow (ASYNC)
└── summarize_conversation()  # Auto-title generator
```

---

## 🔧 Configuration Flow

```
Environment Variables (.env)
    │
    ├─ OPENAI_API_KEY
    ├─ OPENAI_MODEL (gpt-3.5-turbo)
    ├─ EMBEDDING_MODEL (text-embedding-3-small)
    │
    ↓
settings.py (Django)
    │
    ├─ INSTALLED_APPS += 'apps.assistant'
    ├─ RAG_CONFIG = {...}
    │
    ↓
services.py (RAG Logic)
    │
    ├─ OpenAIEmbeddings(api_key, model)
    ├─ ChatOpenAI(api_key, model, temperature)
    │
    ↓
Models (Database)
    │
    ├─ Document → DocumentChunk (pgvector)
    └─ Conversation → Message
```

---

## 📈 Data Flow (Fase B+)

```
User Message
    │
    ↓
views.chat_message()
    │
    ├─→ HelixAssistant.chat()
    │   │
    │   ├─→ RAGPipeline.retrieve_context(query)
    │   │   │
    │   │   ├─ OpenAI.embed_query(query) → embedding vector
    │   │   │
    │   │   ├─ pgvector similarity search
    │   │   │   SELECT * FROM documentchunk
    │   │   │   ORDER BY embedding <-> query_embedding
    │   │   │   LIMIT k
    │   │   │
    │   │   └─ Return top-K DocumentChunks
    │   │
    │   ├─→ RAGPipeline.build_prompt(query, context)
    │   │   └─ Format: SystemPrompt + Context + Query
    │   │
    │   ├─→ ChatOpenAI.astream(prompt) → Response (streaming)
    │   │
    │   └─→ Create Message record
    │       ├─ role='assistant'
    │       ├─ content=response
    │       └─ context_sources=[...]
    │
    └─→ Return response to client (HTMX)
```

---

## 🗄️ Database Schema (pgvector)

```sql
-- Document Table
CREATE TABLE assistant_document (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    source_path VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    content_type VARCHAR(50),
    version VARCHAR(20) DEFAULT '1.0',
    is_active BOOLEAN DEFAULT TRUE,
    ingested_at TIMESTAMP AUTO_NOW_ADD,
    updated_at TIMESTAMP AUTO_NOW,
    company_id BIGINT REFERENCES core_company,
    -- INDEX: (company_id, is_active), (source_path)
);

-- DocumentChunk Table (com pgvector!)
CREATE TABLE assistant_documentchunk (
    id BIGSERIAL PRIMARY KEY,
    document_id BIGINT REFERENCES assistant_document ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536),              -- ← PGVECTOR FIELD!
    token_count INTEGER DEFAULT 0,
    embedding_model VARCHAR(100),
    created_at TIMESTAMP AUTO_NOW_ADD,
    updated_at TIMESTAMP AUTO_NOW,
    -- UNIQUE: (document_id, chunk_index)
    -- INDEX: (document_id, chunk_index)
);

-- Conversation Table
CREATE TABLE assistant_conversation (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES auth_user,
    company_id BIGINT REFERENCES core_company,
    title VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP AUTO_NOW_ADD,
    updated_at TIMESTAMP AUTO_NOW,
    -- INDEX: (user_id, company_id, -created_at)
);

-- Message Table
CREATE TABLE assistant_message (
    id BIGSERIAL PRIMARY KEY,
    conversation_id BIGINT REFERENCES assistant_conversation ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,  -- user|assistant|system
    content TEXT NOT NULL,
    context_sources JSONB DEFAULT '[]',
    tokens_used INTEGER DEFAULT 0,
    created_at TIMESTAMP AUTO_NOW_ADD,
    updated_at TIMESTAMP AUTO_NOW,
    -- INDEX: (conversation_id, created_at), (role)
);

-- HelixConfig Table
CREATE TABLE assistant_helixconfig (
    id BIGSERIAL PRIMARY KEY,
    company_id BIGINT REFERENCES core_company UNIQUE,
    is_enabled BOOLEAN DEFAULT TRUE,
    system_prompt TEXT,
    max_context_chunks INTEGER DEFAULT 5,
    temperature FLOAT DEFAULT 0.3,
    enable_citation BOOLEAN DEFAULT TRUE,
    similarity_threshold FLOAT DEFAULT 0.7,
    created_at TIMESTAMP AUTO_NOW_ADD,
    updated_at TIMESTAMP AUTO_NOW,
);

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;
```

---

## 🔄 Admin Interface

```
Django Admin
│
├── Assistant
│   ├── Documents
│   │   ├── List View: [title | source_path | company | is_active | ingested_at]
│   │   ├── Search: title, source_path, content
│   │   ├── Filter: company, is_active, content_type
│   │   └── Fieldsets: Info, Content, Metadata, Audit
│   │
│   ├── Document Chunks
│   │   ├── List View: [document | chunk_index | token_count | embedding_model | created_at]
│   │   ├── Search: document__title, content
│   │   ├── Filter: document__company, embedding_model
│   │   └── Readonly: created_at, updated_at
│   │
│   ├── Conversations
│   │   ├── List View: [user | title | company | is_active | created_at | message_count]
│   │   ├── Search: user__username, title
│   │   ├── Filter: company, is_active
│   │   └── Custom: message_count() method
│   │
│   ├── Messages
│   │   ├── List View: [conversation | role | content_preview | tokens_used | created_at]
│   │   ├── Search: conversation__user__username, content
│   │   ├── Filter: conversation__company, role
│   │   └── Custom: content_preview() truncated to 100 chars
│   │
│   └── Helix Configuration
│       ├── List View: [company | is_enabled | temperature | max_context_chunks]
│       ├── Filter: company, is_enabled
│       ├── Fieldsets: Config, System Prompt, Response Settings, Features
│       └── Readonly: created_at, updated_at
```

---

## 📝 URL Routing

```
URLs: apps/assistant/urls.py (app_name='assistant')

GET  /chat/                              → chat_interface()
GET  /chat/window/                       → chat_window()
POST /api/chat/message/                  → chat_message()
GET  /api/chat/history/<int:id>/         → get_conversation_history()
POST /api/chat/new/                      → create_conversation()
GET  /api/documents/                     → list_documents()
POST /api/documents/ingest/              → ingest_documents()

(Não integrado em config/urls.py - fazer em Fase C)
```

---

## 🎨 Onyx Color Palette (Fase C)

```css
--color-primary:    #00080D  /* Black */
--color-secondary:  #274B59  /* Teal */
--color-tertiary:   #122E40  /* Navy */
--color-text:       #D0E5F2  /* Light Blue */

Helix Chat Colors:
--user-message:     bg-blue-600 text-white
--assistant:        bg-teal-100 text-gray-900
--citation:         text-blue-600 underline
```

---

**✅ Fase A Architecture Complete**  
**🚀 Ready for Fase B Implementation**

Próximo: Implementar RAG services em `apps/assistant/services.py`
