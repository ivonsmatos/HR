"""
Assistant App - RAG-based Executive Secretary

This app provides a conversational RAG (Retrieval-Augmented Generation) assistant
that can ingest company documents, store them in pgvector embeddings, and answer
queries in the context of the knowledge base.

Modules:
    - models: Database schemas for documents, chunks, conversations, and messages
    - apps: Django app configuration
    - admin: Django admin interface
    - services: RAG logic and LLM interactions
    - views: API endpoints for chat and document management
    - urls: URL routing
"""

default_app_config = 'apps.assistant.apps.AssistantConfig'
