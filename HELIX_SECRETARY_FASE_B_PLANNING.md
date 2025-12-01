# Helix Secretary - Fase B (Planejamento)

**Status**: Pronto para Fase B - RAG Services Implementation  
**Complexidade**: Alta (RAG pipeline + embeddings + vector search)  
**Tempo Estimado**: 4-6 horas

---

## 📋 Objetivos Fase B

Implementar o **core RAG (Retrieval-Augmented Generation)** logic:

1. **DocumentIngestion** - Ingerir docs, chunking, embeddings
2. **RAGPipeline** - Busca por similaridade no pgvector
3. **HelixAssistant** - Conversa inteligente com contexto

---

## 🎯 Tarefas Fase B

### Task B1: DocumentIngestion.ingest_documents()

**Arquivo**: `apps/assistant/services.py` - classe `DocumentIngestion`

```python
@classmethod
def ingest_documents(cls, company_id: int) -> Dict[str, int]:
    """
    Implementar pipeline completo:
    1. discover_documents() → listar docs/
    2. parse_document() → ler cada arquivo
    3. chunk_text() → dividir em chunks
    4. generate_embeddings() → OpenAI embeddings
    5. Criar Document + DocumentChunk records
    6. Retornar stats {'documents_ingested': N, 'chunks_created': M}
    """
```

**Sub-tasks**:

- [ ] B1.1 - Implementar `discover_documents()`

  - Buscar `.md`, `.txt`, `.html` em `docs/`
  - Filtrar por tipo de conteúdo
  - Return: List[Path]

- [ ] B1.2 - Implementar `parse_document(file_path)`

  - Ler arquivo com encoding utf-8
  - Detectar tipo (markdown/text/html)
  - Extrair frontmatter de .md se existir
  - Return: (content, content_type)

- [ ] B1.3 - Implementar `chunk_text(content)`

  - Usar `RecursiveCharacterTextSplitter(chunk_size=1000, overlap=200)`
  - Preservar contexto com separadores: `\n\n`, `\n`, `.`, ` `
  - Return: List[str]

- [ ] B1.4 - Implementar `generate_embeddings(chunks)` ⭐ ASYNC

  - Chamar `openai.Embedding.create()` com batching
  - Usar modelo: `text-embedding-3-small`
  - Tratar rate limits e retry
  - Return: List[List[float]] (1536-dim vectors)

- [ ] B1.5 - Implementar lógica transacional
  - Criar `Document` record com metadata
  - Criar `DocumentChunk` records com embedding + content
  - Salvar `token_count` estimado
  - Transação atômica (rollback on error)
  - Return: stats com contadores

---

### Task B2: RAGPipeline.retrieve_context() ⭐ CRITICAL

**Arquivo**: `apps/assistant/services.py` - classe `RAGPipeline`

```python
@staticmethod
def retrieve_context(
    query: str,
    company_id: int,
    k: int = 5,
    threshold: float = 0.7
) -> List[DocumentChunk]:
    """
    Implementar pgvector similarity search
    Query embedding → Find similar chunks → Return top-K
    """
```

**Sub-tasks**:

- [ ] B2.1 - Query embedding

  - Chamar `embeddings.embed_query(query)`
  - Return: List[float] (1536 dims)

- [ ] B2.2 - pgvector similarity search (Raw SQL)

  ```sql
  SELECT * FROM assistant_documentchunk dc
  JOIN assistant_document d ON dc.document_id = d.id
  WHERE d.company_id = %s AND d.is_active = true
  ORDER BY dc.embedding <-> %s  -- pgvector distance operator
  LIMIT %s
  ```

  - Usar `django.db.connection.cursor()`
  - Passar embedding como numpy array ou list
  - Return: queryset or list

- [ ] B2.3 - Filtrar por threshold

  - Implementar cálculo de cosine similarity
  - Descartar chunks com similaridade < threshold
  - Return: List[DocumentChunk]

- [ ] B2.4 - Adicionar relevância contextual
  - Priorizar chunks da mesmo documento (continuidade)
  - Considerar recency (documentos mais novos)
  - Final ranking: similarity score + context boost

---

### Task B3: RAGPipeline.build_prompt()

**Arquivo**: `apps/assistant/services.py` - classe `RAGPipeline`

```python
@staticmethod
def build_prompt(
    query: str,
    context_chunks: List[DocumentChunk],
    system_prompt: str
) -> str:
    """
    Construir prompt estruturado para LLM
    """
```

**Sub-tasks**:

- [ ] B3.1 - Format context chunks

  ```
  Context:
  [DOC: documento.md - Chunk 3]
  {chunk_content}
  ---
  [DOC: outro.md - Chunk 1]
  {chunk_content}
  ```

- [ ] B3.2 - Adicionar source citations

  - Incluir file path, chunk index, relevância score
  - Exemplo: `[Fonte: docs/setup.md (90% relevante)]`

- [ ] B3.3 - Estruturar prompt final

  ```
  {system_prompt}

  Contexto relevante da base de conhecimento:
  {formatted_context}

  Pergunta: {query}

  Resposta (base-se no contexto acima):
  ```

- [ ] B3.4 - Token estimation
  - Estimar tokens do prompt (safety margin)
  - Truncar context se exceder max_tokens
  - Return: prompt_string

---

### Task B4: HelixAssistant.chat() ⭐ ASYNC

**Arquivo**: `apps/assistant/services.py` - classe `HelixAssistant`

```python
@staticmethod
async def chat(user_message: str, conversation: Conversation) -> str:
    """
    Chat flow completo: message → retrieve → prompt → LLM → save → return
    """
```

**Sub-tasks**:

- [ ] B4.1 - Create user Message record

  - `Message.objects.create(conversation, role='user', content=user_message)`
  - Salvar `context_sources=[]` inicialmente

- [ ] B4.2 - Retrieve context

  - Chamar `RAGPipeline.retrieve_context(user_message, conversation.company_id, k=5)`
  - Store references para depois

- [ ] B4.3 - Build conversation history (últimas 5 messages)

  - Incluir histórico recente para coerência
  - Format: `[{"role": "user/assistant", "content": "..."}]`

- [ ] B4.4 - Build full prompt

  - Chamar `RAGPipeline.build_prompt(user_message, context_chunks, system_prompt)`

- [ ] B4.5 - Call OpenAI LLM ⭐ STREAMING

  - Usar `ChatOpenAI.astream()` para streaming
  - Acumular resposta em tempo real
  - Track tokens (prompt_tokens + completion_tokens)

- [ ] B4.6 - Extract citations

  - Parse resposta para identificar `[Fonte: ...]`
  - Build `context_sources = [{"document_id": X, "chunk_index": Y, "snippet": "..."}]`

- [ ] B4.7 - Create assistant Message record

  - `Message.objects.create(conversation, role='assistant', content=response, context_sources=...)`
  - Salvar `tokens_used = tokens_from_llm`

- [ ] B4.8 - Return response
  - Return: assistant message content

---

### Task B5: Celery Tasks (Background Processing)

**Arquivo**: `apps/assistant/tasks.py` (NOVO)

```python
from celery import shared_task

@shared_task
def ingest_documents_task(company_id: int):
    """Background ingestion task"""
    from .services import DocumentIngestion
    return DocumentIngestion.ingest_documents(company_id)

@shared_task
def batch_embeddings_task(chunk_ids: List[int]):
    """Generate embeddings for multiple chunks"""
    # TODO: Batch OpenAI embedding calls
    pass

@shared_task
def cleanup_old_conversations_task():
    """Archive conversations older than 30 days"""
    # TODO: Archive logic
    pass
```

- [ ] B5.1 - Criar `apps/assistant/tasks.py`
- [ ] B5.2 - Implementar ingest_documents_task com retry logic
- [ ] B5.3 - Implementar batch_embeddings_task
- [ ] B5.4 - Registrar no Celery beat (scheduler)

---

### Task B6: Update Views with RAG Logic

**Arquivo**: `apps/assistant/views.py`

- [ ] B6.1 - Implementar `chat_message` endpoint

  - POST `/api/chat/message/` com `{conversation_id, message}`
  - Chamar `HelixAssistant.chat()`
  - Return: `{assistant_response, context_sources}`

- [ ] B6.2 - Implementar `ingest_documents` endpoint

  - POST `/api/documents/ingest/` (admin only)
  - Chamar `ingest_documents_task.delay(company_id)`
  - Return: `{status: 'queued', task_id, ...}`

- [ ] B6.3 - Implementar `create_conversation`
  - POST `/api/chat/new/` com `{title (optional)}`
  - Auto-generate title from first message later
  - Return: `{conversation_id, title}`

---

### Task B7: Error Handling & Logging

**Arquivo**: `apps/assistant/services.py`

- [ ] B7.1 - Add comprehensive error handling

  - OpenAI API errors (rate limits, auth, network)
  - Database errors (concurrent access, constraints)
  - Embedding generation failures

- [ ] B7.2 - Add logging

  - Debug: ingestion progress
  - Info: chunk counts, embedding stats
  - Warning: partial failures, rate limits
  - Error: critical failures with traceback

- [ ] B7.3 - Add retry mechanisms
  - Exponential backoff para OpenAI calls
  - Max retries: 3
  - Timeout: 30s per request

---

### Task B8: Testing (Unit + Integration)

**Arquivo**: `tests/test_assistant_services.py` (NOVO)

- [ ] B8.1 - Test DocumentIngestion

  - Mock document files
  - Verify chunking logic
  - Mock OpenAI embeddings

- [ ] B8.2 - Test RAGPipeline

  - Mock database queries
  - Verify similarity search ranking
  - Test prompt building

- [ ] B8.3 - Test HelixAssistant

  - Mock LLM responses
  - Verify conversation state
  - Test citation extraction

- [ ] B8.4 - Integration tests
  - End-to-end: ingest → query → response
  - Test with real (or mocked) OpenAI API
  - Verify database state consistency

---

## 🔧 Configuration Required

### Environment Variables

```bash
# .env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-3.5-turbo
EMBEDDING_MODEL=text-embedding-3-small

# Optional
SIMILARITY_THRESHOLD=0.7
MAX_CONTEXT_CHUNKS=5
LLM_TEMPERATURE=0.3
```

### settings.py Addition

```python
# RAG Configuration
RAG_CONFIG = {
    'chunk_size': 1000,
    'chunk_overlap': 200,
    'max_context_chunks': 5,
    'similarity_threshold': 0.7,
    'temperature': 0.3,
}
```

---

## 📊 Implementation Order

1. **B1** - DocumentIngestion (foundation)
2. **B2** - RAGPipeline.retrieve_context (critical)
3. **B3** - RAGPipeline.build_prompt (supporting)
4. **B4** - HelixAssistant.chat (main flow)
5. **B5** - Celery tasks (background)
6. **B6** - Update views (API endpoints)
7. **B7** - Error handling (robustness)
8. **B8** - Testing (quality assurance)

---

## ⏱️ Time Estimate per Task

| Task           | Estimate     | Priority   |
| -------------- | ------------ | ---------- |
| B1 (Ingestion) | 90 min       | ⭐⭐⭐     |
| B2 (Retrieval) | 60 min       | ⭐⭐⭐     |
| B3 (Prompting) | 30 min       | ⭐⭐       |
| B4 (Chat)      | 90 min       | ⭐⭐⭐     |
| B5 (Celery)    | 45 min       | ⭐⭐       |
| B6 (Views)     | 45 min       | ⭐⭐       |
| B7 (Errors)    | 30 min       | ⭐         |
| B8 (Tests)     | 60 min       | ⭐⭐       |
| **Total**      | **~450 min** | **(7.5h)** |

---

## 🚀 Success Criteria Fase B

- [x] Ingest documents from `docs/` folder
- [x] Generate OpenAI embeddings for all chunks
- [x] Retrieve relevant context via pgvector similarity search
- [x] Build contextual prompts with citations
- [x] Generate LLM responses with conversation context
- [x] Track tokens and usage statistics
- [x] Handle errors gracefully with retries
- [x] Full test coverage (unit + integration)
- [x] API endpoints functional and tested

---

**Pronto para Fase B?** 🚀  
Execute quando ambiente estiver pronto com deps instaladas.
