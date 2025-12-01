"""
Initial migration for Assistant app
Creates: Document, DocumentChunk, Conversation, Message, HelixConfig tables
"""

from django.db import migrations, models
import django.db.models.deletion
from django.contrib.postgres.fields import ArrayField


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('core', '0001_initial'),  # Dependency on core app for Company
    ]

    operations = [
        # Enable pgvector extension
        migrations.RunSQL(
            "CREATE EXTENSION IF NOT EXISTS vector;",
            "DROP EXTENSION IF EXISTS vector;",
        ),
        
        # Create Document table
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text="Document title (e.g., 'Installation Guide')", max_length=255)),
                ('source_path', models.CharField(help_text="Original file path (e.g., 'docs/setup.md')", max_length=500)),
                ('content', models.TextField(help_text='Full document content')),
                ('content_type', models.CharField(choices=[('markdown', 'Markdown'), ('text', 'Plain Text'), ('html', 'HTML')], default='markdown', max_length=50)),
                ('version', models.CharField(default='1.0', help_text='Document version', max_length=20)),
                ('is_active', models.BooleanField(default=True, help_text='Include in RAG knowledge base')),
                ('ingested_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='auth.user')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='auth.user')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.company')),
            ],
            options={
                'verbose_name': 'Document',
                'verbose_name_plural': 'Documents',
                'ordering': ['-ingested_at'],
            },
        ),
        
        # Create DocumentChunk table
        migrations.CreateModel(
            name='DocumentChunk',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chunk_index', models.IntegerField(help_text='Sequential chunk number within document')),
                ('content', models.TextField(help_text='Text content of this chunk')),
                ('embedding', ArrayField(base_field=models.FloatField(), blank=True, help_text='OpenAI embedding vector (1536 dimensions for text-embedding-3-small)', null=True, size=1536)),
                ('token_count', models.IntegerField(default=0, help_text='Token count for this chunk')),
                ('embedding_model', models.CharField(default='text-embedding-3-small', help_text='OpenAI model used for embedding', max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chunks', to='assistant.document')),
            ],
            options={
                'verbose_name': 'Document Chunk',
                'verbose_name_plural': 'Document Chunks',
                'ordering': ['document', 'chunk_index'],
                'unique_together': {('document', 'chunk_index')},
            },
        ),
        
        # Create Conversation table
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, help_text='Auto-generated conversation title', max_length=255)),
                ('is_active', models.BooleanField(default=True, help_text='Mark as archived')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='auth.user')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='auth.user')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assistant_conversations', to='auth.user')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.company')),
            ],
            options={
                'verbose_name': 'Conversation',
                'verbose_name_plural': 'Conversations',
                'ordering': ['-created_at'],
            },
        ),
        
        # Create Message table
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('user', 'User'), ('assistant', 'Assistant (Helix)'), ('system', 'System')], help_text='Who sent the message', max_length=20)),
                ('content', models.TextField(help_text='Message content')),
                ('context_sources', models.JSONField(blank=True, default=list, help_text='Documents/chunks used for response (RAG context)')),
                ('tokens_used', models.IntegerField(default=0, help_text='OpenAI tokens consumed by this message')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('conversation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='assistant.conversation')),
            ],
            options={
                'verbose_name': 'Message',
                'verbose_name_plural': 'Messages',
                'ordering': ['created_at'],
            },
        ),
        
        # Create HelixConfig table
        migrations.CreateModel(
            name='HelixConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_enabled', models.BooleanField(default=True, help_text='Enable Helix for this company')),
                ('system_prompt', models.TextField(default='Você é o Secretário Virtual do sistema Onyx Helix. Responda de forma concisa, profissional e sempre baseando-se estritamente no contexto fornecido. Se não souber a resposta, diga que precisa de ajuda de um humano.', help_text='System prompt for LLM (Portuguese)')),
                ('max_context_chunks', models.IntegerField(default=5, help_text='Maximum number of document chunks to use as context')),
                ('temperature', models.FloatField(default=0.3, help_text='LLM temperature (0.0 to 1.0)')),
                ('enable_citation', models.BooleanField(default=True, help_text='Include source citations in responses')),
                ('similarity_threshold', models.FloatField(default=0.7, help_text='Minimum similarity score for relevant chunks (0.0 to 1.0)')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='auth.user')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='auth.user')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.company')),
            ],
            options={
                'verbose_name': 'Helix Configuration',
                'verbose_name_plural': 'Helix Configurations',
                'unique_together': {('company',)},
            },
        ),
        
        # Add indexes
        migrations.AddIndex(
            model_name='document',
            index=models.Index(fields=['company', 'is_active'], name='assistant_document_company_is_active_idx'),
        ),
        migrations.AddIndex(
            model_name='document',
            index=models.Index(fields=['source_path'], name='assistant_document_source_path_idx'),
        ),
        migrations.AddIndex(
            model_name='documentchunk',
            index=models.Index(fields=['document', 'chunk_index'], name='assistant_documentchunk_document_chunk_idx'),
        ),
        migrations.AddIndex(
            model_name='conversation',
            index=models.Index(fields=['user', 'company', '-created_at'], name='assistant_conversation_user_company_created_idx'),
        ),
        migrations.AddIndex(
            model_name='message',
            index=models.Index(fields=['conversation', 'created_at'], name='assistant_message_conversation_created_idx'),
        ),
        migrations.AddIndex(
            model_name='message',
            index=models.Index(fields=['role'], name='assistant_message_role_idx'),
        ),
    ]
