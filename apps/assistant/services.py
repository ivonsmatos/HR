"""
RAG Services for Helix Secretary - FASE B

Core RAG pipeline implementation using:
- LangChain for orchestration
- OpenAI embeddings for vector representation
- PostgreSQL pgvector for similarity search
- LangChain-Postgres for vector storage integration

Modules to implement:
1. DocumentIngestion - Read docs/, parse, chunk, embed
2. RAGPipeline - Query processing with context retrieval
3. HelixAssistant - LLM interaction with conversational context
"""

import os
import logging
from typing import List, Dict, Optional, Tuple
from pathlib import Path

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import RetrievalQA
from langchain_postgres import PGVector

from .models import Document, DocumentChunk, Conversation, Message, HelixConfig

logger = logging.getLogger(__name__)

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
DOCS_FOLDER = Path(__file__).parent.parent.parent / "docs"

# LangChain initialization
embeddings = OpenAIEmbeddings(
    api_key=OPENAI_API_KEY,
    model="text-embedding-3-small"
)

llm = ChatOpenAI(
    api_key=OPENAI_API_KEY,
    model="gpt-3.5-turbo",
    temperature=0.3,
)


class DocumentIngestion:
    """
    Handles document ingestion pipeline
    
    Process:
    1. Discover docs in docs/ folder
    2. Parse content (markdown, text, html)
    3. Split into chunks with overlap
    4. Generate embeddings via OpenAI
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
        
        return sorted(documents)
    
    @staticmethod
    def parse_document(file_path: Path) -> Tuple[str, str]:
        """
        Parse document and return (content, content_type)
        
        TODO: Implement:
        - .md parsing with frontmatter extraction
        - .html parsing with BeautifulSoup
        - .txt plain text reading
        """
        content = file_path.read_text(encoding='utf-8')
        content_type = 'markdown' if file_path.suffix == '.md' else 'text'
        
        return content, content_type
    
    @staticmethod
    def chunk_text(content: str) -> List[str]:
        """
        Split text into chunks using RecursiveCharacterTextSplitter
        
        Preserves context with overlap
        """
        splitter = RecursiveCharacterTextSplitter(
            **DocumentIngestion.TEXT_SPLITTER_CONFIG
        )
        chunks = splitter.split_text(content)
        return chunks
    
    @staticmethod
    async def generate_embeddings(chunks: List[str]) -> List[List[float]]:
        """
        Generate embeddings for chunks using OpenAI
        
        Returns list of embedding vectors (1536 dimensions)
        """
        # TODO: Batch embeddings generation
        # embeddings_response = await embeddings.embed_documents(chunks)
        # return embeddings_response
        pass
    
    @classmethod
    def ingest_documents(cls, company_id: int) -> Dict[str, int]:
        """
        Main ingestion pipeline
        
        Returns stats: {'documents_ingested': N, 'chunks_created': M, 'errors': E}
        """
        stats = {'documents_ingested': 0, 'chunks_created': 0, 'errors': 0}
        
        # TODO: Implement full pipeline:
        # 1. Loop through discovered documents
        # 2. Parse each document
        # 3. Chunk content
        # 4. Generate embeddings
        # 5. Create Document + DocumentChunk records
        # 6. Track progress and errors
        
        return stats


class RAGPipeline:
    """
    Retrieval-Augmented Generation pipeline
    
    Process:
    1. Convert query to embedding
    2. Find similar chunks using pgvector similarity search
    3. Build context from top-K similar chunks
    4. Format prompt with context
    5. Call LLM for response
    """
    
    @staticmethod
    def retrieve_context(
        query: str,
        company_id: int,
        k: int = 5,
        threshold: float = 0.7
    ) -> List[DocumentChunk]:
        """
        Retrieve most relevant document chunks
        
        Uses pgvector similarity search:
        SELECT * FROM assistant_documentchunk
        WHERE embedding <-> query_embedding < distance_threshold
        ORDER BY embedding <-> query_embedding
        LIMIT k
        
        TODO: Implement with django.db.connection.cursor() and psycopg2
        """
        # TODO: Implement similarity search
        # 1. Generate query embedding
        # 2. Calculate cosine similarity distance
        # 3. Filter by threshold
        # 4. Sort by distance
        # 5. Return top K
        pass
    
    @staticmethod
    def build_prompt(
        query: str,
        context_chunks: List[DocumentChunk],
        system_prompt: str
    ) -> str:
        """
        Build LLM prompt with RAG context
        
        Format:
        {system_prompt}
        
        Context:
        {chunk1}
        ---
        {chunk2}
        ...
        
        Question: {query}
        Answer:
        """
        # TODO: Format context with citations
        pass
    
    @staticmethod
    async def answer_query(
        query: str,
        conversation: Conversation,
        context_chunks: Optional[List[DocumentChunk]] = None
    ) -> Tuple[str, List[str]]:
        """
        Process query and return answer with sources
        
        TODO: Implement:
        1. Retrieve context if not provided
        2. Build prompt
        3. Call LLM with streaming
        4. Track tokens used
        5. Extract citations
        6. Create Message record
        """
        pass


class HelixAssistant:
    """
    Executive Secretary conversational interface
    
    Persona: "Secretário Executivo"
    - Formal, concise, professional tone
    - Always cite sources for information
    - Escalate to humans when uncertain
    - Remember conversation context
    """
    
    @staticmethod
    def get_config(company_id: int) -> HelixConfig:
        """Get Helix configuration for company"""
        config, _ = HelixConfig.objects.get_or_create(company_id=company_id)
        return config
    
    @staticmethod
    async def chat(
        user_message: str,
        conversation: Conversation,
    ) -> str:
        """
        Process user message and return assistant response
        
        TODO: Implement conversation flow:
        1. Create user Message record
        2. Retrieve RAG context
        3. Build prompt with history
        4. Generate response
        5. Create assistant Message record
        6. Return response
        """
        pass
    
    @staticmethod
    def summarize_conversation(conversation: Conversation) -> str:
        """Generate auto title from first few messages"""
        messages = conversation.messages.filter(role='user').values_list('content', flat=True)[:2]
        if not messages:
            return "New Conversation"
        
        first_msg = messages[0][:50]
        return f"{first_msg}..." if len(first_msg) < 50 else first_msg


# ===== Helper Functions =====

def get_connection_string() -> str:
    """Build pgvector connection string from DATABASE_URL"""
    # TODO: Extract from django settings.DATABASES
    pass


def enable_pgvector_extension():
    """Ensure pgvector extension is enabled in PostgreSQL"""
    # Already done in migration, but can be called explicitly
    pass


def calculate_similarity(
    query_embedding: List[float],
    chunk_embedding: List[float]
) -> float:
    """Calculate cosine similarity between two vectors"""
    import math
    dot_product = sum(q * c for q, c in zip(query_embedding, chunk_embedding))
    norm_q = math.sqrt(sum(q ** 2 for q in query_embedding))
    norm_c = math.sqrt(sum(c ** 2 for c in chunk_embedding))
    return dot_product / (norm_q * norm_c) if norm_q and norm_c else 0.0


# ===== Celery Tasks (Async) =====
# These will be implemented for background processing

# TODO: Implement Celery tasks:
# - ingest_documents_task() - batch document ingestion
# - process_query_task() - background query processing
# - batch_embeddings_task() - generate embeddings for multiple chunks
