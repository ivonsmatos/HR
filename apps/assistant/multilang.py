"""
Model Quantization & Multi-Language Support (FASE E+)

Features:
- Model quantization (Q4, Q5, Q8) for memory efficiency
- Multi-language support (PT-BR, EN, ES, FR, DE)
- Automatic language detection
- Language-specific prompts and responses
"""

import os
import logging
from typing import Dict, List, Optional
from enum import Enum
from langdetect import detect, detect_langs

logger = logging.getLogger(__name__)


class QuantizationType(Enum):
    """Model quantization levels"""
    Q2 = "q2"      # 2-bit (2-4 GB memory, low quality)
    Q3 = "q3"      # 3-bit (3-5 GB memory, fair quality)
    Q4 = "q4"      # 4-bit (5-8 GB memory, good quality)
    Q5 = "q5"      # 5-bit (8-12 GB memory, high quality)
    Q8 = "q8"      # 8-bit (12-16 GB memory, very high quality)
    FP16 = "fp16"  # Float16 (16+ GB memory, full precision)


class Language(Enum):
    """Supported languages"""
    PORTUGUESE_BR = "pt-BR"
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    ITALIAN = "it"
    CHINESE = "zh"
    JAPANESE = "ja"


class ModelQuantizer:
    """Manage model quantization for memory efficiency"""
    
    # Quantization mapping to Ollama model tags
    QUANTIZATION_MODELS = {
        QuantizationType.Q2: "qwen2.5:7b-instruct-q2_K",
        QuantizationType.Q3: "qwen2.5:7b-instruct-q3_K",
        QuantizationType.Q4: "qwen2.5:14b-instruct-q4_K_M",
        QuantizationType.Q5: "qwen2.5:14b-instruct-q5_K_M",
        QuantizationType.Q8: "qwen2.5:14b-instruct-q8_0",
        QuantizationType.FP16: "qwen2.5:14b",  # Original model
    }
    
    # Performance estimates
    PERFORMANCE_PROFILE = {
        QuantizationType.Q2: {
            'memory_gb': 3,
            'speedup': '2.5x',
            'quality': 'Low',
            'use_case': 'Lightweight, edge devices'
        },
        QuantizationType.Q3: {
            'memory_gb': 5,
            'speedup': '2x',
            'quality': 'Fair',
            'use_case': 'Mobile, limited resources'
        },
        QuantizationType.Q4: {
            'memory_gb': 8,
            'speedup': '1.5x',
            'quality': 'Good',
            'use_case': 'Recommended default'
        },
        QuantizationType.Q5: {
            'memory_gb': 12,
            'speedup': '1.2x',
            'quality': 'High',
            'use_case': 'Server, accuracy important'
        },
        QuantizationType.Q8: {
            'memory_gb': 16,
            'speedup': '1x',
            'quality': 'Very High',
            'use_case': 'Production, maximum quality'
        },
        QuantizationType.FP16: {
            'memory_gb': 28,
            'speedup': '1x',
            'quality': 'Maximum',
            'use_case': 'Full precision (GPU recommended)'
        },
    }
    
    @staticmethod
    def get_recommended_quantization(available_memory_gb: int) -> QuantizationType:
        """
        Recommend quantization level based on available memory
        
        Args:
            available_memory_gb: Available system memory in GB
        
        Returns:
            Recommended QuantizationType
        """
        if available_memory_gb >= 28:
            return QuantizationType.FP16
        elif available_memory_gb >= 16:
            return QuantizationType.Q8
        elif available_memory_gb >= 12:
            return QuantizationType.Q5
        elif available_memory_gb >= 8:
            return QuantizationType.Q4
        elif available_memory_gb >= 5:
            return QuantizationType.Q3
        else:
            return QuantizationType.Q2
    
    @staticmethod
    def get_model_tag(quantization: QuantizationType) -> str:
        """Get Ollama model tag for quantization level"""
        return ModelQuantizer.QUANTIZATION_MODELS.get(
            quantization,
            ModelQuantizer.QUANTIZATION_MODELS[QuantizationType.Q4]
        )
    
    @staticmethod
    def get_performance_info(quantization: QuantizationType) -> Dict:
        """Get performance information for quantization level"""
        return ModelQuantizer.PERFORMANCE_PROFILE.get(
            quantization,
            ModelQuantizer.PERFORMANCE_PROFILE[QuantizationType.Q4]
        )


class LanguageManager:
    """Manage multi-language support"""
    
    # System prompts by language
    SYSTEM_PROMPTS = {
        Language.PORTUGUESE_BR: """Você é o assistente virtual do sistema SyncRH.
Você é profissional, direto e prestativo.
Use estritamente o contexto fornecido para responder.
Se a resposta não estiver no contexto, diga que não sabe.
Responda sempre em Português do Brasil.
Mantenha respostas concisas e objetivas.""",
        
        Language.ENGLISH: """You are the virtual assistant of the SyncRH system.
You are professional, direct and helpful.
Use strictly the provided context to answer.
If the answer is not in the context, say you don't know.
Always respond in English.
Keep responses concise and objective.""",
        
        Language.SPANISH: """Eres el asistente virtual del sistema SyncRH.
Eres profesional, directo y servicial.
Usa estrictamente el contexto proporcionado para responder.
Si la respuesta no está en el contexto, di que no sabes.
Siempre responde en español.
Mantén las respuestas concisas y objetivas.""",
        
        Language.FRENCH: """Vous êtes l'assistant virtuel du système SyncRH.
Vous êtes professionnel, direct et utile.
Utilisez strictement le contexte fourni pour répondre.
Si la réponse n'est pas dans le contexte, dites que vous ne savez pas.
Répondez toujours en français.
Gardez les réponses concises et objectives.""",
        
        Language.GERMAN: """Sie sind der virtuelle Assistent des SyncRH-Systems.
Sie sind professionell, direkt und hilfreich.
Verwenden Sie ausschließlich den bereitgestellten Kontext, um zu antworten.
Wenn die Antwort nicht im Kontext vorhanden ist, sagen Sie, dass Sie es nicht wissen.
Antworten Sie immer auf Deutsch.
Halten Sie Antworten prägnant und sachlich.""",
    }
    
    # Citation formats by language
    CITATION_FORMATS = {
        Language.PORTUGUESE_BR: "Fonte: {title} (Seção {index})",
        Language.ENGLISH: "Source: {title} (Section {index})",
        Language.SPANISH: "Fuente: {title} (Sección {index})",
        Language.FRENCH: "Source: {title} (Section {index})",
        Language.GERMAN: "Quelle: {title} (Abschnitt {index})",
    }
    
    # Messages by language
    MESSAGES = {
        Language.PORTUGUESE_BR: {
            'no_results': 'Nenhum resultado encontrado para sua busca.',
            'thinking': 'SyncRH está processando...',
            'error': 'Ocorreu um erro ao processar sua solicitação.',
            'welcome': 'Olá! Sou o SyncRH. Como posso ajudá-lo?',
        },
        Language.ENGLISH: {
            'no_results': 'No results found for your search.',
            'thinking': 'SyncRH is processing...',
            'error': 'An error occurred while processing your request.',
            'welcome': 'Hello! I\'m Helix. How can I help you?',
        },
        Language.SPANISH: {
            'no_results': 'No se encontraron resultados para su búsqueda.',
            'thinking': 'SyncRH está processando...',
            'error': 'Ocurrió un error al procesar su solicitud.',
            'welcome': '¡Hola! Soy SyncRH. ¿Cómo puedo ayudarte?',
        },
        Language.FRENCH: {
            'no_results': 'Aucun résultat trouvé pour votre recherche.',
            'thinking': 'SyncRH traite...',
            'error': 'Une erreur s\'est produite lors du traitement de votre demande.',
            'welcome': 'Bonjour! Je suis SyncRH. Comment puis-je vous aider?',
        },
        Language.GERMAN: {
            'no_results': 'Keine Ergebnisse für Ihre Suche gefunden.',
            'thinking': 'SyncRH verarbeitet...',
            'error': 'Ein Fehler ist bei der Verarbeitung Ihrer Anfrage aufgetreten.',
            'welcome': 'Hallo! Ich bin SyncRH. Wie kann ich dir helfen?',
        },
    }
    
    @staticmethod
    def detect_language(text: str) -> Language:
        """
        Detect language from text
        
        Args:
            text: Input text to detect language
        
        Returns:
            Detected Language enum
        """
        try:
            lang_code = detect(text)
            
            # Map langdetect codes to our Language enum
            mapping = {
                'pt': Language.PORTUGUESE_BR,
                'en': Language.ENGLISH,
                'es': Language.SPANISH,
                'fr': Language.FRENCH,
                'de': Language.GERMAN,
                'it': Language.ITALIAN,
                'zh-cn': Language.CHINESE,
                'ja': Language.JAPANESE,
            }
            
            return mapping.get(lang_code, Language.PORTUGUESE_BR)
        
        except Exception as e:
            logger.warning(f"Language detection failed: {e}")
            return Language.PORTUGUESE_BR  # Default to Portuguese
    
    @staticmethod
    def get_system_prompt(language: Language) -> str:
        """Get system prompt for language"""
        return LanguageManager.SYSTEM_PROMPTS.get(
            language,
            LanguageManager.SYSTEM_PROMPTS[Language.PORTUGUESE_BR]
        )
    
    @staticmethod
    def get_citation_format(language: Language) -> str:
        """Get citation format for language"""
        return LanguageManager.CITATION_FORMATS.get(
            language,
            LanguageManager.CITATION_FORMATS[Language.PORTUGUESE_BR]
        )
    
    @staticmethod
    def get_message(language: Language, key: str) -> str:
        """Get localized message"""
        messages = LanguageManager.MESSAGES.get(
            language,
            LanguageManager.MESSAGES[Language.PORTUGUESE_BR]
        )
        return messages.get(key, '')
    
    @staticmethod
    def get_supported_languages() -> List[Dict[str, str]]:
        """Get list of supported languages"""
        return [
            {'code': lang.value, 'name': lang.name}
            for lang in Language
        ]


# Integration with Helix services

def get_quantized_model_config(quantization: QuantizationType) -> Dict[str, str]:
    """Get Ollama model configuration for quantization level"""
    return {
        'LLM_MODEL': ModelQuantizer.get_model_tag(quantization),
        'EMBEDDING_MODEL': 'nomic-embed-text',  # Embeddings don't change
    }


def format_citation_by_language(title: str, index: int, language: Language) -> str:
    """Format citation according to language"""
    format_str = LanguageManager.get_citation_format(language)
    return format_str.format(title=title, index=index)
