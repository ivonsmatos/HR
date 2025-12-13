"""
SyncRH - Recrutamento e Seleção - Serializers
==============================================
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.core.base.validators import validate_cpf, validate_phone, validate_cep

from .models import (
    Vaga, Candidato, Candidatura, Entrevista,
    AvaliacaoEntrevista, PerfilCargo, EtapaSelecao
)

User = get_user_model()


class PerfilCargoSerializer(serializers.ModelSerializer):
    """Serializer para perfil de cargo"""
    
    class Meta:
        model = PerfilCargo
        fields = [
            'id', 'cargo', 'competencias_tecnicas', 'competencias_comportamentais',
            'formacao_minima', 'experiencia_minima', 'certificacoes_desejaveis',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class VagaListSerializer(serializers.ModelSerializer):
    """Serializer resumido para listagem de vagas"""
    departamento_nome = serializers.CharField(source='departamento.nome', read_only=True)
    cargo_nome = serializers.CharField(source='cargo.titulo', read_only=True)
    total_candidaturas = serializers.SerializerMethodField()
    
    class Meta:
        model = Vaga
        fields = [
            'id', 'codigo', 'titulo', 'departamento_nome', 'cargo_nome',
            'status', 'tipo_contrato', 'regime_trabalho', 'quantidade_vagas',
            'total_candidaturas', 'data_abertura', 'data_previsao_fechamento'
        ]
    
    def get_total_candidaturas(self, obj):
        return obj.candidaturas.count()


class VagaDetailSerializer(serializers.ModelSerializer):
    """Serializer detalhado para vaga"""
    departamento_nome = serializers.CharField(source='departamento.nome', read_only=True)
    cargo_nome = serializers.CharField(source='cargo.titulo', read_only=True)
    recrutador_nome = serializers.CharField(source='recrutador.get_full_name', read_only=True)
    perfil_cargo_data = PerfilCargoSerializer(source='perfil_cargo', read_only=True)
    candidaturas_por_etapa = serializers.SerializerMethodField()
    
    class Meta:
        model = Vaga
        fields = [
            'id', 'codigo', 'titulo', 'descricao', 'departamento', 'departamento_nome',
            'cargo', 'cargo_nome', 'perfil_cargo', 'perfil_cargo_data',
            'status', 'tipo_contrato', 'regime_trabalho', 'carga_horaria',
            'quantidade_vagas', 'salario_minimo', 'salario_maximo', 'salario_ofertado',
            'beneficios', 'requisitos_obrigatorios', 'requisitos_desejaveis',
            'cidade', 'estado', 'pais', 'recrutador', 'recrutador_nome',
            'prioridade', 'confidencial', 'aceita_pcd', 'data_abertura',
            'data_previsao_fechamento', 'data_fechamento', 'motivo_fechamento',
            'candidaturas_por_etapa', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['codigo', 'data_abertura', 'created_at', 'updated_at']
    
    def get_candidaturas_por_etapa(self, obj):
        return obj.candidaturas.values('etapa_atual').annotate(
            total=serializers.IntegerField()
        )


class CandidatoSerializer(serializers.ModelSerializer):
    """Serializer para candidato"""
    nome_completo = serializers.SerializerMethodField()
    idade = serializers.SerializerMethodField()
    
    class Meta:
        model = Candidato
        fields = [
            'id', 'nome', 'sobrenome', 'nome_completo', 'cpf', 'data_nascimento',
            'idade', 'email', 'telefone', 'celular', 'linkedin', 'portfolio',
            'cidade', 'estado', 'pais', 'resumo_profissional', 'curriculo',
            'foto', 'formacao_academica', 'experiencia_profissional',
            'habilidades', 'idiomas', 'pretensao_salarial', 'disponibilidade_inicio',
            'origem', 'indicado_por', 'is_pcd', 'tipo_deficiencia',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_nome_completo(self, obj):
        return f"{obj.nome} {obj.sobrenome}"
    
    def get_idade(self, obj):
        if obj.data_nascimento:
            from datetime import date
            today = date.today()
            return today.year - obj.data_nascimento.year - (
                (today.month, today.day) < (obj.data_nascimento.month, obj.data_nascimento.day)
            )
        return None
    
    def validate_cpf(self, value):
        if value:
            validate_cpf(value)
        return value
    
    def validate_telefone(self, value):
        if value:
            validate_phone(value)
        return value


class EtapaSelecaoSerializer(serializers.ModelSerializer):
    """Serializer para etapas de seleção"""
    
    class Meta:
        model = EtapaSelecao
        fields = [
            'id', 'vaga', 'nome', 'ordem', 'tipo', 'descricao',
            'obrigatoria', 'peso', 'is_active'
        ]


class CandidaturaListSerializer(serializers.ModelSerializer):
    """Serializer resumido para listagem de candidaturas"""
    candidato_nome = serializers.CharField(source='candidato.nome', read_only=True)
    vaga_titulo = serializers.CharField(source='vaga.titulo', read_only=True)
    
    class Meta:
        model = Candidatura
        fields = [
            'id', 'candidato', 'candidato_nome', 'vaga', 'vaga_titulo',
            'etapa_atual', 'status', 'nota_geral', 'data_candidatura', 'data_atualizacao'
        ]


class CandidaturaDetailSerializer(serializers.ModelSerializer):
    """Serializer detalhado para candidatura"""
    candidato_data = CandidatoSerializer(source='candidato', read_only=True)
    vaga_data = VagaListSerializer(source='vaga', read_only=True)
    avaliacoes = serializers.SerializerMethodField()
    
    class Meta:
        model = Candidatura
        fields = [
            'id', 'candidato', 'candidato_data', 'vaga', 'vaga_data',
            'etapa_atual', 'status', 'nota_geral', 'observacoes',
            'carta_apresentacao', 'resposta_perguntas', 'match_perfil',
            'aprovado_rh', 'aprovado_gestor', 'proposta_enviada',
            'proposta_aceita', 'data_candidatura', 'data_atualizacao',
            'data_proposta', 'data_resposta_proposta', 'motivo_reprovacao',
            'avaliacoes', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['data_candidatura', 'created_at', 'updated_at']
    
    def get_avaliacoes(self, obj):
        return AvaliacaoEntrevistaSerializer(
            obj.avaliacoes.all(), many=True
        ).data


class EntrevistaSerializer(serializers.ModelSerializer):
    """Serializer para entrevista"""
    candidatura_info = serializers.SerializerMethodField()
    entrevistadores_nomes = serializers.SerializerMethodField()
    
    class Meta:
        model = Entrevista
        fields = [
            'id', 'candidatura', 'candidatura_info', 'tipo', 'data_hora',
            'duracao_prevista', 'local', 'link_online', 'entrevistadores',
            'entrevistadores_nomes', 'status', 'parecer', 'nota',
            'proxima_etapa', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_candidatura_info(self, obj):
        return {
            'candidato': obj.candidatura.candidato.nome,
            'vaga': obj.candidatura.vaga.titulo
        }
    
    def get_entrevistadores_nomes(self, obj):
        return list(obj.entrevistadores.values_list('first_name', flat=True))


class AvaliacaoEntrevistaSerializer(serializers.ModelSerializer):
    """Serializer para avaliação de entrevista"""
    avaliador_nome = serializers.CharField(source='avaliador.get_full_name', read_only=True)
    
    class Meta:
        model = AvaliacaoEntrevista
        fields = [
            'id', 'candidatura', 'entrevista', 'avaliador', 'avaliador_nome',
            'competencia', 'nota', 'peso', 'observacoes',
            'pontos_fortes', 'pontos_melhoria', 'recomendacao',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_nota(self, value):
        if value < 0 or value > 10:
            raise serializers.ValidationError("A nota deve estar entre 0 e 10")
        return value
