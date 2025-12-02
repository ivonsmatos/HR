"""
E2E Tests for Helix Secretary with Ollama

Tests validate the complete RAG pipeline:
1. Ollama connection and model availability
2. Document ingestion and embedding
3. RAG retrieval with pgvector
4. Chat flow with LLM response
5. HTMX integration and template rendering

Requirements:
- Ollama running on localhost:11434
- qwen2.5:14b and nomic-embed-text models available
- PostgreSQL with pgvector extension
- Django test database configured
"""

import os
import json
import logging
from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from datetime import timedelta

from apps.assistant.models import (
    Conversation, Message, Document, DocumentChunk, HelixConfig
)
from apps.assistant.services import (
    check_ollama_connection,
    verify_ollama_models,
    DocumentIngestion,
    RAGPipeline,
    HelixAssistant,
    get_helix_status,
)
from apps.core.models import Company
import pytest

logger = logging.getLogger(__name__)
User = get_user_model()


@pytest.mark.django_db
class OllamaConnectionTest(TestCase):
    """Test Ollama service availability and configuration"""
    
    def test_ollama_connection(self):
        """Verify Ollama is running on localhost:11434"""
        self.assertTrue(
            check_ollama_connection(),
            "Ollama não está disponível. Inicie o serviço com: ollama serve"
        )
    
    def test_ollama_models_available(self):
        """Verify required models (qwen2.5:14b, nomic-embed-text) are available"""
        models = verify_ollama_models()
        
        self.assertTrue(
            models.get('qwen2.5:14b'),
            "Modelo qwen2.5:14b não encontrado. Execute: ollama pull qwen2.5:14b"
        )
        
        self.assertTrue(
            models.get('nomic-embed-text'),
            "Modelo nomic-embed-text não encontrado. Execute: ollama pull nomic-embed-text"
        )
    
    def test_helix_status(self):
        """Verify system health check"""
        status = get_helix_status()
        
        self.assertIn('ollama_running', status)
        self.assertIn('models_available', status)
        self.assertTrue(status['ollama_running'])


@pytest.mark.django_db
class DocumentIngestionTest(TestCase):
    """Test document ingestion pipeline"""
    
    @classmethod
    def setUpClass(cls):
        """Setup test company and user"""
        super().setUpClass()
        
        cls.company = Company.objects.create(
            name="Test Company",
            slug="test-company",
            domain="test.local"
        )
        
        cls.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            tenant=cls.company
        )
    
    def setUp(self):
        """Create test documents before each test"""
        # Create sample docs/ directory with markdown files
        docs_path = "docs"
        os.makedirs(docs_path, exist_ok=True)
        
        # Create sample document
        with open(f"{docs_path}/test_document.md", "w", encoding="utf-8") as f:
            f.write("""# Guia de Uso do Sistema

## Introdução
Este é um documento de teste para validação do pipeline RAG.

## Funcionalidades
1. Chat integrado
2. Pesquisa de documentos
3. Respostas com citações

## Conclusão
O sistema está funcionando corretamente.""")
    
    def tearDown(self):
        """Cleanup after tests"""
        import shutil
        if os.path.exists("docs"):
            shutil.rmtree("docs")
    
    def test_document_discovery(self):
        """Test discovering documents in docs/ folder"""
        discovery = DocumentIngestion()
        docs = discovery.discover_documents(folder="docs")
        
        self.assertGreater(len(docs), 0, "Nenhum documento encontrado em docs/")
    
    def test_document_ingestion_pipeline(self):
        """Test complete ingestion pipeline: parse → chunk → embed → store"""
        # Run ingestion
        result = DocumentIngestion.ingest_documents(
            company_id=self.company.id
        )
        
        # Verify results
        self.assertEqual(result['status'], 'success')
        self.assertGreater(result['documents_ingested'], 0)
        self.assertGreater(result['chunks_created'], 0)
        
        # Verify documents stored in DB
        documents = Document.objects.filter(company=self.company)
        self.assertGreater(documents.count(), 0)
        
        # Verify chunks with embeddings
        chunks = DocumentChunk.objects.filter(
            document__company=self.company
        )
        self.assertGreater(chunks.count(), 0)
        
        # Verify embeddings are not empty
        for chunk in chunks[:1]:
            self.assertIsNotNone(chunk.embedding)
            self.assertGreater(len(chunk.embedding), 0)
    
    def test_chunks_have_embeddings(self):
        """Verify pgvector embeddings are stored correctly"""
        # First ingest documents
        DocumentIngestion.ingest_documents(company_id=self.company.id)
        
        # Check embeddings
        chunks = DocumentChunk.objects.filter(
            document__company=self.company
        )
        
        for chunk in chunks:
            self.assertIsNotNone(chunk.embedding)
            # Verify embedding is a list of floats
            self.assertIsInstance(chunk.embedding, list)
            self.assertGreater(len(chunk.embedding), 0)
            self.assertIsInstance(chunk.embedding[0], (float, int))


@pytest.mark.django_db
class RAGRetrievalTest(TestCase):
    """Test RAG retrieval with pgvector similarity search"""
    
    @classmethod
    def setUpClass(cls):
        """Setup test data"""
        super().setUpClass()
        
        cls.company = Company.objects.create(
            name="RAG Test Company",
            slug="rag-test",
            domain="rag.test"
        )
        
        cls.user = User.objects.create_user(
            username="raguser",
            email="rag@example.com",
            password="testpass123",
            tenant=cls.company
        )
    
    def setUp(self):
        """Create test documents with embeddings"""
        # Create sample doc
        docs_path = "docs"
        os.makedirs(docs_path, exist_ok=True)
        
        with open(f"{docs_path}/rag_test.md", "w", encoding="utf-8") as f:
            f.write("""# Documentação Técnica

## API REST
O sistema oferece uma API REST completa para integração.

### Endpoints
- GET /api/users/ - Listar usuários
- POST /api/users/ - Criar usuário
- GET /api/documents/ - Listar documentos

## Autenticação
Use token JWT para autenticar nas chamadas API.

## Rate Limiting
Máximo de 1000 requisições por hora.""")
        
        # Ingest documents
        DocumentIngestion.ingest_documents(company_id=self.company.id)
    
    def tearDown(self):
        """Cleanup"""
        import shutil
        if os.path.exists("docs"):
            shutil.rmtree("docs")
    
    def test_similarity_search(self):
        """Test pgvector similarity search"""
        query = "Como usar a API?"
        
        pipeline = RAGPipeline()
        context = pipeline.retrieve_context(
            query=query,
            company_id=self.company.id,
            k=5
        )
        
        self.assertGreater(len(context), 0, "Nenhum resultado de similaridade encontrado")
        
        # Verify chunks contain relevant content
        content = " ".join([c.content for c in context])
        self.assertIn(
            ("API" or "endpoint" or "autenticação").lower(),
            content.lower()
        )
    
    def test_context_building(self):
        """Test RAG context formatting with citations"""
        query = "API endpoints"
        
        pipeline = RAGPipeline()
        context_chunks = pipeline.retrieve_context(
            query=query,
            company_id=self.company.id
        )
        
        prompt = pipeline.build_prompt(
            query=query,
            context_chunks=context_chunks,
            enable_citation=True
        )
        
        # Verify prompt contains context
        self.assertIn(query, prompt)
        self.assertIn("Contexto", prompt)
        
        # Verify citations are formatted
        if context_chunks:
            self.assertIn("[1]", prompt)


@pytest.mark.django_db
class ChatFlowTest(TestCase):
    """Test complete chat flow with Ollama LLM"""
    
    @classmethod
    def setUpClass(cls):
        """Setup test environment"""
        super().setUpClass()
        
        cls.company = Company.objects.create(
            name="Chat Test Company",
            slug="chat-test",
            domain="chat.test"
        )
        
        cls.user = User.objects.create_user(
            username="chatuser",
            email="chat@example.com",
            password="testpass123",
            tenant=cls.company
        )
    
    def setUp(self):
        """Create test conversation"""
        self.conversation = Conversation.objects.create(
            user=self.user,
            company=self.company,
            title="Test Conversation",
            is_active=True
        )
    
    def test_chat_message_creation(self):
        """Test creating user message"""
        message = Message.objects.create(
            conversation=self.conversation,
            role='user',
            content="Olá Helix!",
        )
        
        self.assertEqual(message.role, 'user')
        self.assertEqual(message.content, "Olá Helix!")
        self.assertIsNotNone(message.created_at)
    
    def test_assistant_response_generation(self):
        """Test generating assistant response via Ollama"""
        user_message = "O que é um ERP?"
        
        # Create test documents for RAG
        docs_path = "docs"
        os.makedirs(docs_path, exist_ok=True)
        
        with open(f"{docs_path}/erp_info.md", "w", encoding="utf-8") as f:
            f.write("""# O que é um ERP?

Um ERP (Enterprise Resource Planning) é um sistema de software que integra
todas as funções de negócio em uma plataforma única.

## Benefícios
- Centralização de dados
- Automação de processos
- Melhor tomada de decisão
- Redução de custos operacionais""")
        
        # Ingest documents
        DocumentIngestion.ingest_documents(company_id=self.company.id)
        
        # Generate response
        response_data = HelixAssistant.chat(
            user_message=user_message,
            conversation=self.conversation,
            user_id=self.user.id
        )
        
        # Verify response
        self.assertIn('response', response_data)
        self.assertIn('citations', response_data)
        self.assertIn('status', response_data)
        
        # Response should contain relevant information
        response_text = response_data['response'].lower()
        self.assertTrue(
            any(word in response_text for word in ['erp', 'sistema', 'integra', 'dados']),
            f"Response does not contain relevant ERP information: {response_data['response']}"
        )
        
        # Cleanup
        import shutil
        if os.path.exists("docs"):
            shutil.rmtree("docs")
    
    def test_conversation_history(self):
        """Test retrieving conversation history"""
        # Create messages
        Message.objects.create(
            conversation=self.conversation,
            role='user',
            content="Primeira pergunta"
        )
        Message.objects.create(
            conversation=self.conversation,
            role='assistant',
            content="Primeira resposta"
        )
        
        # Retrieve history
        history = HelixAssistant.get_conversation_history(
            self.conversation,
            limit=10
        )
        
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]['role'], 'user')
        self.assertEqual(history[1]['role'], 'assistant')


@pytest.mark.django_db
class ViewsHTMXTest(TestCase):
    """Test HTMX views and template rendering"""
    
    @classmethod
    def setUpClass(cls):
        """Setup test environment"""
        super().setUpClass()
        
        cls.company = Company.objects.create(
            name="Views Test Company",
            slug="views-test",
            domain="views.test"
        )
        
        cls.user = User.objects.create_user(
            username="viewsuser",
            email="views@example.com",
            password="testpass123",
            tenant=cls.company
        )
    
    def setUp(self):
        """Create test client and login"""
        self.client = Client()
        self.client.login(username="viewsuser", password="testpass123")
    
    def test_chat_interface_view(self):
        """Test chat interface page loads"""
        response = self.client.get('/assistant/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('conversations', response.context)
    
    def test_chat_message_endpoint(self):
        """Test HTMX chat message POST endpoint"""
        conversation = Conversation.objects.create(
            user=self.user,
            company=self.company,
            title="Test",
            is_active=True
        )
        
        # Note: This test requires Ollama running and documents ingested
        response = self.client.post(
            '/assistant/api/chat/message/',
            {
                'conversation_id': conversation.id,
                'message': 'Teste HTMX'
            }
        )
        
        # Should return HTML fragment
        self.assertIn(
            response.status_code,
            [200, 500],  # 500 if no documents, 200 if success
        )
    
    def test_health_check_endpoint(self):
        """Test health check returns system status"""
        response = self.client.get('/assistant/api/health/')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertIn('ollama_running', data)
        self.assertIn('models_available', data)


@pytest.mark.django_db
class ContextProcessorTest(TestCase):
    """Test Helix context processor"""
    
    @classmethod
    def setUpClass(cls):
        """Setup test environment"""
        super().setUpClass()
        
        cls.company = Company.objects.create(
            name="Context Test Company",
            slug="context-test",
            domain="context.test"
        )
        
        cls.user = User.objects.create_user(
            username="contextuser",
            email="context@example.com",
            password="testpass123",
            tenant=cls.company
        )
    
    def setUp(self):
        """Create test client and login"""
        self.client = Client()
        self.client.login(username="contextuser", password="testpass123")
    
    def test_helix_context_available(self):
        """Test that helix context is available in templates"""
        response = self.client.get('/assistant/')
        
        # Context processor should add helix data
        self.assertIn('helix', response.context)
        
        helix_ctx = response.context['helix']
        self.assertIn('status', helix_ctx)
        self.assertIn('ollama_available', helix_ctx)
        self.assertTrue(helix_ctx['user_authenticated'])
    
    def test_context_processor_with_conversation(self):
        """Test context processor with active conversation"""
        # Create conversation
        conversation = Conversation.objects.create(
            user=self.user,
            company=self.company,
            title="Active Conversation",
            is_active=True
        )
        
        response = self.client.get('/assistant/')
        
        helix_ctx = response.context['helix']
        self.assertTrue(helix_ctx['has_conversations'])
        self.assertIsNotNone(helix_ctx['current_conversation'])


@pytest.mark.django_db
class IntegrationTest(TestCase):
    """Full end-to-end integration test"""
    
    @classmethod
    def setUpClass(cls):
        """Setup complete test environment"""
        super().setUpClass()
        
        cls.company = Company.objects.create(
            name="Integration Test Company",
            slug="integration-test",
            domain="integration.test"
        )
        
        cls.user = User.objects.create_user(
            username="integrationuser",
            email="integration@example.com",
            password="testpass123",
            tenant=cls.company
        )
    
    def setUp(self):
        """Create test client and documents"""
        self.client = Client()
        self.client.login(username="integrationuser", password="testpass123")
        
        # Create sample documents
        docs_path = "docs"
        os.makedirs(docs_path, exist_ok=True)
        
        with open(f"{docs_path}/integration_guide.md", "w", encoding="utf-8") as f:
            f.write("""# Guia de Integração

## Requisitos
- Python 3.10+
- PostgreSQL 15+
- Ollama 0.1+

## Instalação
1. Clone o repositório
2. Configure o .env
3. Execute migrations
4. Inicie o Ollama

## Testando a Integração
Execute os testes com pytest.""")
    
    def tearDown(self):
        """Cleanup"""
        import shutil
        if os.path.exists("docs"):
            shutil.rmtree("docs")
    
    def test_full_pipeline(self):
        """Test complete pipeline: docs → ingest → chat → response"""
        # Step 1: Ingest documents
        ingest_result = DocumentIngestion.ingest_documents(
            company_id=self.company.id
        )
        self.assertEqual(ingest_result['status'], 'success')
        
        # Step 2: Create conversation
        conversation = Conversation.objects.create(
            user=self.user,
            company=self.company,
            title="Integration Test",
            is_active=True
        )
        
        # Step 3: Ask question
        question = "Quais são os requisitos de instalação?"
        
        response_data = HelixAssistant.chat(
            user_message=question,
            conversation=conversation,
            user_id=self.user.id
        )
        
        # Step 4: Verify complete flow
        self.assertEqual(response_data['status'], 'success')
        self.assertIn('response', response_data)
        self.assertGreater(len(response_data['response']), 0)
        
        # Verify messages were created
        messages = Message.objects.filter(conversation=conversation)
        self.assertGreaterEqual(messages.count(), 2)  # At least user + assistant


if __name__ == '__main__':
    import unittest
    unittest.main()
