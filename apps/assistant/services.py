"""
RAG Services for SyncRH - FASE B (Ollama Stack)

Core RAG pipeline implementation using:
- LangChain for orchestration
- Ollama (qwen2.5:14b) for LLM generation (localhost:11434)
- Nomic embeddings for vector representation
- PostgreSQL pgvector for similarity search
- LangChain-Postgres for vector storage integration

Hardware: 32GB RAM (sufficient for 14B model)

Modules:
1. HelixConfig - Configuration management
2. DocumentIngestion - Read docs/, parse, chunk, embed (async)
3. RAGPipeline - Query processing with pgvector retrieval
4. HelixAssistant - LLM interaction with conversational memory
"""

import os
import logging
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import json

try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_community.embeddings import OllamaEmbeddings
    from langchain_community.llms import Ollama
    from langchain.chains import RetrievalQA
    from langchain_postgres import PGVector
    from langchain_core.documents import Document as LangChainDocument
    from langchain.prompts import PromptTemplate
except ImportError as e:
    # Langchain optional dependency
    RecursiveCharacterTextSplitter = None
    OllamaEmbeddings = None
    Ollama = None
    RetrievalQA = None
    PGVector = None
    LangChainDocument = None
    PromptTemplate = None

from .models import Document, DocumentChunk, Conversation, Message, HelixConfig

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

# Ollama Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen2.5:14b")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")

# Database
DATABASE_URL = os.getenv("DATABASE_URL")
DOCS_FOLDER = Path(__file__).parent.parent.parent / "docs"

# LangChain initialization - Ollama Stack
try:
    embeddings = OllamaEmbeddings(
        base_url=OLLAMA_BASE_URL,
        model=EMBEDDING_MODEL,
        show_progress=True,
    )
    logger.info(f"✓ Ollama Embeddings initialized ({EMBEDDING_MODEL})")
except Exception as e:
    logger.error(f"✗ Failed to initialize Ollama Embeddings: {e}")
    embeddings = None

try:
    llm = Ollama(
        base_url=OLLAMA_BASE_URL,
        model=LLM_MODEL,
        temperature=0.1,  # Low temperature for technical accuracy
        top_k=40,
        top_p=0.9,
        num_ctx=4096,  # Context window
    )
    logger.info(f"✓ Ollama LLM initialized ({LLM_MODEL})")
except Exception as e:
    logger.error(f"✗ Failed to initialize Ollama LLM: {e}")
    llm = None

# System Prompt for Helix
HELIX_SYSTEM_PROMPT = """Você é o assistente virtual do sistema SyncRH. 
Você é profissional, direto e prestativo. 
Use estritamente o contexto fornecido para responder. 
Se a resposta não estiver no contexto, diga que não sabe. 
Responda sempre em Português do Brasil.
Mantenha respostas concisas (máximo 3-5 linhas) e objetivas."""


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def check_ollama_connection() -> bool:
    """Verify Ollama is running and accessible."""
    import requests
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Ollama connection failed: {e}")
        return False


def get_vector_db() -> Optional[PGVector]:
    """Initialize or retrieve vector database connection."""
    if not DATABASE_URL or not embeddings:
        return None
    
    try:
        return PGVector(
            connection_string=DATABASE_URL,
            embedding_function=embeddings,
            collection_name="helix_knowledge_base",
        )
    except Exception as e:
        logger.error(f"Failed to initialize PGVector: {e}")
        return None


class HelixConfig:
    """Configuration manager for Helix Secretary per tenant."""
    
    @staticmethod
    def get_config(company_id: int) -> Dict:
        """Get Helix configuration for tenant."""
        try:
            config = HelixConfig.objects.get(company_id=company_id)
            return {
                "is_enabled": config.is_enabled,
                "system_prompt": config.system_prompt,
                "max_context_chunks": config.max_context_chunks,
                "temperature": config.temperature,
                "enable_citation": config.enable_citation,
                "similarity_threshold": config.similarity_threshold,
            }
        except:
            # Return defaults
            return {
                "is_enabled": True,
                "system_prompt": HELIX_SYSTEM_PROMPT,
                "max_context_chunks": 5,
                "temperature": 0.1,
                "enable_citation": True,
                "similarity_threshold": 0.7,
            }


class DocumentIngestion:
    """
    Handles document ingestion pipeline using Ollama embeddings
    
    Process:
    1. Discover docs in docs/ folder
    2. Parse content (markdown, text, html)
    3. Split into chunks with overlap
    4. Generate embeddings via Ollama (nomic-embed-text)
    5. Store in PostgreSQL with pgvector
    """
    
    TEXT_SPLITTER_CONFIG = {
        'chunk_size': 1000,
        'chunk_overlap': 200,
        'separators': ['\n\n', '\n', '.', ' '],
    }
    
    @staticmethod
    def discover_documents(folder: Path = DOCS_FOLDER) -> List[Path]:
        """
        Discover all documents in docs/ folder
        
        Supported formats: .md, .txt, .html
        """
        if not folder.exists():
            logger.warning(f"Docs folder not found: {folder}")
            return []
        
        documents = []
        for ext in ['.md', '.txt', '.html']:
            documents.extend(folder.rglob(f'*{ext}'))
        
        logger.info(f"✓ Found {len(documents)} documents in {folder}")
        return sorted(documents)
    
    @staticmethod
    def parse_document(file_path: Path) -> Tuple[str, str]:
        """
        Parse document and return (content, content_type)
        
        Supports:
        - .md (Markdown with frontmatter)
        - .html (HTML content)
        - .txt (Plain text)
        """
        try:
            content = file_path.read_text(encoding='utf-8')
            
            if file_path.suffix == '.md':
                content_type = 'markdown'
            elif file_path.suffix == '.html':
                content_type = 'html'
            else:
                content_type = 'text'
            
            logger.debug(f"✓ Parsed {file_path.name} ({content_type})")
            return content, content_type
            
        except Exception as e:
            logger.error(f"✗ Error parsing {file_path}: {e}")
            return "", "text"
    
    @staticmethod
    def chunk_text(content: str) -> List[str]:
        """
        Split text into chunks using RecursiveCharacterTextSplitter
        
        Preserves context with overlap for better retrieval
        """
        splitter = RecursiveCharacterTextSplitter(
            **DocumentIngestion.TEXT_SPLITTER_CONFIG
        )
        chunks = splitter.split_text(content)
        logger.debug(f"✓ Generated {len(chunks)} chunks")
        return chunks
    
    @staticmethod
    def ingest_documents(company_id: int) -> Dict[str, int]:
        """
        Main ingestion pipeline - synchronous version
        
        Returns stats: {
            'documents_ingested': N,
            'chunks_created': M,
            'errors': E,
            'status': 'success'|'partial'|'failed'
        }
        
        Process:
        1. Check Ollama connection
        2. Discover documents
        3. Parse each document
        4. Chunk content
        5. Generate embeddings using Ollama
        6. Create Document + DocumentChunk records in DB
        7. Track statistics
        """
        
        if not check_ollama_connection():
            logger.error("✗ Ollama not running at {OLLAMA_BASE_URL}")
            return {
                'documents_ingested': 0,
                'chunks_created': 0,
                'errors': 1,
                'status': 'failed',
                'message': f"Ollama not accessible at {OLLAMA_BASE_URL}"
            }
        
        if not embeddings:
            logger.error("✗ Embeddings not initialized")
            return {
                'documents_ingested': 0,
                'chunks_created': 0,
                'errors': 1,
                'status': 'failed',
                'message': "Embeddings not initialized"
            }
        
        stats = {
            'documents_ingested': 0,
            'chunks_created': 0,
            'errors': 0,
            'status': 'success'
        }
        
        # Discover documents
        doc_paths = DocumentIngestion.discover_documents()
        if not doc_paths:
            logger.warning("No documents found in docs folder")
            stats['message'] = "No documents to ingest"
            return stats
        
        # Get or create company Document objects
        from apps.core.models import Company
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            logger.error(f"✗ Company {company_id} not found")
            stats['errors'] = 1
            stats['status'] = 'failed'
            return stats
        
        # Process each document
        for doc_path in doc_paths:
            try:
                logger.info(f"Processing: {doc_path.name}")
                
                # Parse document
                content, content_type = DocumentIngestion.parse_document(doc_path)
                if not content:
                    stats['errors'] += 1
                    continue
                
                # Create Document record
                document, created = Document.objects.get_or_create(
                    company=company,
                    source_path=str(doc_path.relative_to(DOCS_FOLDER)),
                    defaults={
                        'title': doc_path.stem,
                        'content': content,
                        'content_type': content_type,
                        'version': '1.0',
                        'is_active': True,
                    }
                )
                
                if created:
                    stats['documents_ingested'] += 1
                    logger.info(f"✓ Created Document: {document.title}")
                else:
                    logger.debug(f"  Document already exists: {document.title}")
                
                # Chunk and embed content
                chunks = DocumentIngestion.chunk_text(content)
                
                # Generate embeddings for chunks
                logger.info(f"  Generating embeddings for {len(chunks)} chunks...")
                try:
                    chunk_embeddings = embeddings.embed_documents(chunks)
                    
                    # Create DocumentChunk records
                    for chunk_idx, (chunk_content, embedding_vec) in enumerate(
                        zip(chunks, chunk_embeddings)
                    ):
                        chunk_obj, _ = DocumentChunk.objects.get_or_create(
                            document=document,
                            chunk_index=chunk_idx,
                            defaults={
                                'content': chunk_content,
                                'embedding': embedding_vec,
                                'token_count': len(chunk_content.split()),
                                'embedding_model': EMBEDDING_MODEL,
                            }
                        )
                        stats['chunks_created'] += 1
                    
                    logger.info(f"✓ Created {len(chunks)} chunks for {document.title}")
                    
                except Exception as e:
                    logger.error(f"✗ Error generating embeddings: {e}")
                    stats['errors'] += 1
                    stats['status'] = 'partial'
                    
            except Exception as e:
                logger.error(f"✗ Error processing {doc_path}: {e}")
                stats['errors'] += 1
                stats['status'] = 'partial'
        
        stats['message'] = f"Ingested {stats['documents_ingested']} documents with {stats['chunks_created']} chunks"
        logger.info(f"✓ Ingestion complete: {stats}")
        return stats


class RAGPipeline:
    """
    Retrieval-Augmented Generation pipeline using Ollama
    
    Process:
    1. Convert query to embedding using Ollama (nomic-embed-text)
    2. Find similar chunks using pgvector similarity search
    3. Build context from top-K similar chunks
    4. Format prompt with context
    5. Call Qwen 2.5 LLM for response
    """
    
    @staticmethod
    def retrieve_context(
        query: str,
        company_id: int,
        k: int = 5,
        threshold: float = 0.7
    ) -> List[DocumentChunk]:
        """
        Retrieve most relevant document chunks using pgvector similarity search
        
        Process:
        1. Generate query embedding using Ollama
        2. Find similar chunks using pgvector <-> operator (L2 distance)
        3. Filter by similarity threshold
        4. Return top K chunks sorted by relevance
        
        Args:
            query: User question
            company_id: Tenant identifier
            k: Number of chunks to retrieve
            threshold: Minimum similarity score (0.0 to 1.0)
            
        Returns:
            List of most relevant DocumentChunk objects
        """
        
        if not embeddings or not query.strip():
            return []
        
        try:
            # Generate query embedding
            query_embedding = embeddings.embed_query(query)
            logger.debug(f"✓ Generated query embedding ({len(query_embedding)} dims)")
            
            # Raw SQL for pgvector similarity search
            from django.db import connection
            
            with connection.cursor() as cursor:
                # Using cosine similarity with pgvector
                sql = """
                    SELECT ac.id, ac.document_id, ac.chunk_index, ac.content,
                           ac.embedding, ac.token_count, ac.created_at,
                           (1 - (ac.embedding <=> %s::vector)) as similarity
                    FROM assistant_documentchunk ac
                    JOIN assistant_document ad ON ac.document_id = ad.id
                    WHERE ad.company_id = %s 
                          AND ad.is_active = true
                          AND (1 - (ac.embedding <=> %s::vector)) >= %s
                    ORDER BY similarity DESC
                    LIMIT %s
                """
                
                cursor.execute(sql, [
                    json.dumps(query_embedding),  # Query embedding as JSON vector
                    company_id,
                    json.dumps(query_embedding),
                    threshold,
                    k
                ])
                
                results = cursor.fetchall()
                logger.info(f"✓ Retrieved {len(results)} similar chunks (threshold: {threshold})")
                
                # Convert results to DocumentChunk objects
                chunk_ids = [row[0] for row in results]
                if chunk_ids:
                    chunks = DocumentChunk.objects.filter(id__in=chunk_ids)
                    return list(chunks)
                
                return []
                
        except Exception as e:
            logger.error(f"✗ Error retrieving context: {e}")
            return []
    
    @staticmethod
    def build_prompt(
        query: str,
        context_chunks: List[DocumentChunk],
        system_prompt: str = HELIX_SYSTEM_PROMPT,
        enable_citation: bool = True
    ) -> str:
        """
        Build LLM prompt with RAG context
        
        Format:
        {system_prompt}
        
        Context from documentation:
        [1] {chunk1_content}
        Source: {document_title} (Section {chunk_index})
        ---
        [2] {chunk2_content}
        Source: {document_title} (Section {chunk_index})
        ...
        
        Pergunta: {query}
        Resposta:
        
        Args:
            query: User question
            context_chunks: List of relevant document chunks
            system_prompt: System instruction for model
            enable_citation: Include source references
            
        Returns:
            Formatted prompt string ready for LLM
        """
        
        # Build context section
        context_parts = []
        for idx, chunk in enumerate(context_chunks, 1):
            chunk_text = f"[{idx}] {chunk.content.strip()}"
            context_parts.append(chunk_text)
            
            if enable_citation:
                doc_title = chunk.document.title
                section = f"Seção {chunk.chunk_index}"
                citation = f"Fonte: {doc_title} ({section})"
                context_parts.append(f"  {citation}")
            
            context_parts.append("---")
        
        context_str = "\n".join(context_parts) if context_parts else "[Sem contexto disponível]"
        
        # Build final prompt
        prompt = f"""{system_prompt}

Contexto da documentação:
{context_str}

Pergunta: {query}
Resposta (em Português, concisa e objetiva):"""
        
        logger.debug(f"✓ Built prompt ({len(prompt)} chars, {len(context_chunks)} sources)")
        return prompt
    
    @staticmethod
    def answer_query(
        query: str,
        conversation: Conversation,
        context_chunks: Optional[List[DocumentChunk]] = None,
        use_conversation_history: bool = True
    ) -> Tuple[str, List[Dict]]:
        """
        Process query and return answer with sources (synchronous version)
        
        Process:
        1. Retrieve context if not provided
        2. Build conversation history for context
        3. Build prompt with context
        4. Call Qwen 2.5 LLM
        5. Extract citations from context chunks
        6. Create Message records
        
        Args:
            query: User question
            conversation: Conversation object (contains user, company context)
            context_chunks: Optional pre-retrieved chunks
            use_conversation_history: Include previous messages for context
            
        Returns:
            Tuple of (response_text, citations_list)
            
        Raises:
            ValueError if LLM or embeddings not initialized
        """
        
        if not llm or not embeddings:
            raise ValueError("Ollama LLM or Embeddings not initialized")
        
        try:
            logger.info(f"Processing query: {query[:50]}...")
            
            # Step 1: Retrieve context if not provided
            if context_chunks is None:
                context_chunks = RAGPipeline.retrieve_context(
                    query=query,
                    company_id=conversation.company_id,
                    k=5,
                    threshold=0.7
                )
            
            # Step 2: Get Helix config for this company
            config = HelixConfig.get_config(conversation.company_id)
            
            # Step 3: Build prompt with context
            prompt = RAGPipeline.build_prompt(
                query=query,
                context_chunks=context_chunks,
                system_prompt=config.get("system_prompt", HELIX_SYSTEM_PROMPT),
                enable_citation=config.get("enable_citation", True)
            )
            
            # Step 4: Call Qwen 2.5 LLM
            logger.info("Calling Ollama LLM (qwen2.5:14b)...")
            response = llm.invoke(prompt)
            
            logger.info(f"✓ Generated response ({len(response)} chars)")
            
            # Step 5: Build citations list
            citations = []
            for chunk in context_chunks:
                citations.append({
                    'document_id': chunk.document.id,
                    'title': chunk.document.title,
                    'source_path': chunk.document.source_path,
                    'chunk_index': chunk.chunk_index,
                    'snippet': chunk.content[:200],  # First 200 chars
                })
            
            return response, citations
            
        except Exception as e:
            logger.error(f"✗ Error answering query: {e}")
            raise


class HelixAssistant:
    """
    Executive Secretary conversational interface using Ollama
    
    Persona: "Secretário Executivo"
    - Formal, concise, professional tone
    - Always cite sources for information
    - Escalate to humans when uncertain
    - Remember conversation context
    - Respond in Portuguese (Brazil)
    """
    
    @staticmethod
    def get_config(company_id: int) -> Dict:
        """Get Helix configuration for company"""
        return HelixConfig.get_config(company_id)
    
    @staticmethod
    def chat(
        user_message: str,
        conversation: Conversation,
        user_id: int,
    ) -> Dict:
        """
        Process user message and return assistant response
        
        Conversation flow:
        1. Create user Message record
        2. Retrieve RAG context using pgvector
        3. Build prompt with conversation history + context
        4. Call Qwen 2.5 LLM via Ollama
        5. Create assistant Message record with citations
        6. Return response with metadata
        
        Args:
            user_message: User's query/message
            conversation: Conversation object
            user_id: User ID for message creation
            
        Returns:
            {
                'response': str,           # Assistant response
                'citations': [Dict],       # Source references
                'status': 'success'|'error',
                'processing_time': float,  # Seconds
                'tokens_used': int,        # Approximation
                'message_id': int,         # DB record ID
            }
        """
        
        import time
        from django.contrib.auth.models import User
        
        start_time = time.time()
        
        try:
            logger.info(f"Chat initiated: {user_message[:50]}...")
            
            # Step 1: Create user Message record
            user_obj = User.objects.get(id=user_id)
            user_msg = Message.objects.create(
                conversation=conversation,
                role='user',
                content=user_message,
                context_sources=[],
                tokens_used=0,
            )
            logger.info(f"✓ Created user message: {user_msg.id}")
            
            # Step 2 & 3 & 4: RAG pipeline
            response_text, citations = RAGPipeline.answer_query(
                query=user_message,
                conversation=conversation,
                use_conversation_history=True
            )
            
            # Step 5: Create assistant Message record
            assistant_msg = Message.objects.create(
                conversation=conversation,
                role='assistant',
                content=response_text,
                context_sources=citations,
                tokens_used=0,  # TODO: Implement token counting
            )
            logger.info(f"✓ Created assistant message: {assistant_msg.id}")
            
            # Update conversation title if first message
            if conversation.title is None or conversation.title == '':
                title = HelixAssistant.summarize_conversation(user_message)
                conversation.title = title
                conversation.save()
                logger.info(f"✓ Auto-titled conversation: {title}")
            
            processing_time = time.time() - start_time
            
            return {
                'response': response_text,
                'citations': citations,
                'status': 'success',
                'processing_time': round(processing_time, 2),
                'tokens_used': 0,
                'message_id': assistant_msg.id,
            }
            
        except Exception as e:
            logger.error(f"✗ Chat error: {e}")
            processing_time = time.time() - start_time
            
            return {
                'response': f"Desculpe, ocorreu um erro ao processar sua pergunta: {str(e)}",
                'citations': [],
                'status': 'error',
                'processing_time': round(processing_time, 2),
                'tokens_used': 0,
                'error': str(e),
            }
    
    @staticmethod
    def summarize_conversation(first_message: str, max_length: int = 60) -> str:
        """
        Generate auto title from first message
        
        Args:
            first_message: First user message
            max_length: Maximum title length
            
        Returns:
            Truncated first message as title
        """
        if len(first_message) <= max_length:
            return first_message
        return f"{first_message[:max_length]}..."
    
    @staticmethod
    def get_conversation_history(
        conversation: Conversation,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get recent conversation history
        
        Returns:
            List of {role, content, created_at, citations} for UI rendering
        """
        messages = conversation.messages.order_by('-created_at')[:limit]
        
        history = []
        for msg in reversed(messages):
            history.append({
                'role': msg.role,
                'content': msg.content,
                'created_at': msg.created_at.isoformat(),
                'citations': msg.context_sources,
            })
        
        return history


# ===== Helper Functions =====

def get_database_connection_string() -> str:
    """Extract PostgreSQL connection string from Django settings"""
    from django.conf import settings
    db_config = settings.DATABASES['default']
    
    if db_config['ENGINE'] == 'django_tenants.postgresql_backend':
        return (
            f"postgresql://{db_config['USER']}:{db_config['PASSWORD']}"
            f"@{db_config['HOST']}:{db_config['PORT']}/{db_config['NAME']}"
        )
    return ""


def verify_ollama_models() -> Dict[str, bool]:
    """Verify required Ollama models are available"""
    import requests
    
    models_check = {
        'qwen2.5:14b': False,
        'nomic-embed-text': False,
    }
    
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            available_models = [m['name'].split(':')[0] for m in response.json().get('models', [])]
            for model in models_check:
                model_name = model.split(':')[0]
                models_check[model] = model_name in available_models
    except Exception as e:
        logger.error(f"Error checking models: {e}")
    
    return models_check


def enable_pgvector_extension():
    """Ensure pgvector extension is enabled in PostgreSQL"""
    from django.db import connection
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            logger.info("✓ pgvector extension enabled")
    except Exception as e:
        logger.warning(f"pgvector extension status: {e}")


def calculate_cosine_similarity(
    vec1: List[float],
    vec2: List[float]
) -> float:
    """Calculate cosine similarity between two vectors"""
    import math
    
    if not vec1 or not vec2:
        return 0.0
    
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a ** 2 for a in vec1))
    norm2 = math.sqrt(sum(b ** 2 for b in vec2))
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return dot_product / (norm1 * norm2)


def estimate_tokens(text: str) -> int:
    """Rough token count estimation for text"""
    # Approximate: 1 token ≈ 4 characters (for Portuguese)
    return len(text) // 4


# ===== Status & Health Check =====

def get_helix_status() -> Dict[str, any]:
    """Get system status for monitoring"""
    return {
        'ollama_running': check_ollama_connection(),
        'ollama_url': OLLAMA_BASE_URL,
        'llm_model': LLM_MODEL,
        'embedding_model': EMBEDDING_MODEL,
        'models_available': verify_ollama_models(),
        'embeddings_initialized': embeddings is not None,
        'llm_initialized': llm is not None,
        'database_available': DATABASE_URL is not None,
    }


# ===== Celery Tasks (Background Processing) =====

try:
    from celery import shared_task
    
    @shared_task
    def ingest_documents_task(company_id: int):
        """Background task for document ingestion"""
        logger.info(f"Starting background ingestion for company {company_id}")
        result = DocumentIngestion.ingest_documents(company_id)
        logger.info(f"Ingestion complete: {result}")
        return result
    
    @shared_task
    def batch_embeddings_task(chunk_ids: List[int]):
        """Generate embeddings for multiple chunks"""
        logger.info(f"Generating embeddings for {len(chunk_ids)} chunks")
        # TODO: Implement batch embedding generation
        return {'processed': len(chunk_ids)}
    
    @shared_task
    def cleanup_conversations_task():
        """Archive conversations older than 90 days"""
        from datetime import timedelta
        from django.utils import timezone
        
        cutoff_date = timezone.now() - timedelta(days=90)
        archived = Conversation.objects.filter(
            created_at__lt=cutoff_date,
            is_active=True
        ).update(is_active=False)
        
        logger.info(f"Archived {archived} old conversations")
        return {'archived': archived}
    
except ImportError:
    logger.warning("Celery not available - background tasks disabled")

