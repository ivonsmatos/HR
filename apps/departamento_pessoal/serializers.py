"""
SyncRH - Departamento Pessoal - Serializers
===========================================

Serializers para APIs do módulo Departamento Pessoal.
"""

from rest_framework import serializers
from django.contrib.auth.models import User

from .models import (
    Colaborador, Departamento, Cargo, EscalaTrabalho,
    RegistroPonto, JustificativaPonto, FolhaPagamento,
    ItemFolha, ProcessoAdmissao, DocumentoAdmissao,
    CategoriaDocumento, DocumentoGED, PeriodoAquisitivo,
    SolicitacaoFerias, FeriasColetivas, Contador, ExportacaoContabil
)
from apps.core.base.validators import validate_cpf, validate_phone


class UserSerializer(serializers.ModelSerializer):
    """Serializer para usuário"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class DepartamentoSerializer(serializers.ModelSerializer):
    """Serializer para departamento"""
    total_colaboradores = serializers.IntegerField(read_only=True)
    responsavel_nome = serializers.CharField(source='responsavel.nome_completo', read_only=True)
    
    class Meta:
        model = Departamento
        fields = [
            'id', 'uuid', 'nome', 'codigo', 'descricao',
            'responsavel', 'responsavel_nome', 'total_colaboradores',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at']


class CargoSerializer(serializers.ModelSerializer):
    """Serializer para cargo"""
    
    class Meta:
        model = Cargo
        fields = [
            'id', 'uuid', 'nome', 'codigo', 'descricao',
            'cbo', 'nivel', 'salario_base', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at']


class ColaboradorListSerializer(serializers.ModelSerializer):
    """Serializer resumido para listagem de colaboradores"""
    cargo_nome = serializers.CharField(source='cargo.nome', read_only=True)
    departamento_nome = serializers.CharField(source='departamento.nome', read_only=True)
    
    class Meta:
        model = Colaborador
        fields = [
            'id', 'uuid', 'nome_completo', 'cpf', 'email_pessoal',
            'cargo', 'cargo_nome', 'departamento', 'departamento_nome',
            'data_admissao', 'foto_perfil', 'is_active'
        ]


class ColaboradorSerializer(serializers.ModelSerializer):
    """Serializer completo para colaborador"""
    user = UserSerializer(read_only=True)
    cargo_nome = serializers.CharField(source='cargo.nome', read_only=True)
    departamento_nome = serializers.CharField(source='departamento.nome', read_only=True)
    gestor_nome = serializers.CharField(source='gestor.nome_completo', read_only=True)
    
    class Meta:
        model = Colaborador
        fields = [
            'id', 'uuid', 'user', 'nome_completo', 'cpf',
            'data_nascimento', 'data_admissao', 'data_demissao',
            'cargo', 'cargo_nome', 'departamento', 'departamento_nome',
            'gestor', 'gestor_nome', 'email_pessoal', 'telefone',
            'endereco', 'banco', 'agencia', 'conta', 'tipo_conta',
            'foto_perfil', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at']
    
    def validate_cpf(self, value):
        """Valida CPF"""
        validate_cpf(value)
        return value
    
    def validate_telefone(self, value):
        """Valida telefone"""
        if value:
            validate_phone(value)
        return value


class EscalaTrabalhoSerializer(serializers.ModelSerializer):
    """Serializer para escala de trabalho"""
    
    class Meta:
        model = EscalaTrabalho
        fields = [
            'id', 'uuid', 'nome', 'descricao', 'tipo',
            'carga_horaria_semanal', 'horarios', 'is_active'
        ]


class RegistroPontoSerializer(serializers.ModelSerializer):
    """Serializer para registro de ponto"""
    colaborador_nome = serializers.CharField(source='colaborador.nome_completo', read_only=True)
    
    class Meta:
        model = RegistroPonto
        fields = [
            'id', 'uuid', 'colaborador', 'colaborador_nome',
            'data', 'hora', 'tipo', 'origem', 'localizacao',
            'foto_registro', 'observacao', 'validado', 'created_at'
        ]
        read_only_fields = ['id', 'uuid', 'created_at']


class JustificativaPontoSerializer(serializers.ModelSerializer):
    """Serializer para justificativa de ponto"""
    
    class Meta:
        model = JustificativaPonto
        fields = [
            'id', 'uuid', 'colaborador', 'data', 'tipo',
            'motivo', 'documento', 'status', 'aprovado_por',
            'data_aprovacao', 'observacao_aprovador'
        ]


class ItemFolhaSerializer(serializers.ModelSerializer):
    """Serializer para itens da folha de pagamento"""
    
    class Meta:
        model = ItemFolha
        fields = [
            'id', 'codigo', 'descricao', 'tipo',
            'referencia', 'valor'
        ]


class FolhaPagamentoSerializer(serializers.ModelSerializer):
    """Serializer para folha de pagamento"""
    colaborador_nome = serializers.CharField(source='colaborador.nome_completo', read_only=True)
    itens = ItemFolhaSerializer(many=True, read_only=True)
    
    class Meta:
        model = FolhaPagamento
        fields = [
            'id', 'uuid', 'colaborador', 'colaborador_nome',
            'mes', 'ano', 'salario_base', 'total_proventos',
            'total_descontos', 'salario_liquido', 'status',
            'data_pagamento', 'itens', 'created_at'
        ]
        read_only_fields = ['id', 'uuid', 'created_at']


class ProcessoAdmissaoSerializer(serializers.ModelSerializer):
    """Serializer para processo de admissão"""
    
    class Meta:
        model = ProcessoAdmissao
        fields = [
            'id', 'uuid', 'candidato_nome', 'candidato_cpf',
            'candidato_email', 'cargo_pretendido', 'departamento',
            'salario_proposto', 'data_admissao_prevista',
            'tipo_contrato', 'status', 'etapa_atual',
            'documentos_pendentes', 'observacoes'
        ]


class CategoriaDocumentoSerializer(serializers.ModelSerializer):
    """Serializer para categoria de documento"""
    
    class Meta:
        model = CategoriaDocumento
        fields = ['id', 'nome', 'descricao', 'requer_validade', 'obrigatorio']


class DocumentoGEDSerializer(serializers.ModelSerializer):
    """Serializer para documento GED"""
    colaborador_nome = serializers.CharField(source='colaborador.nome_completo', read_only=True)
    categoria_nome = serializers.CharField(source='categoria.nome', read_only=True)
    
    class Meta:
        model = DocumentoGED
        fields = [
            'id', 'uuid', 'colaborador', 'colaborador_nome',
            'categoria', 'categoria_nome', 'titulo', 'descricao',
            'arquivo', 'data_validade', 'tags', 'is_active'
        ]


class PeriodoAquisitivoSerializer(serializers.ModelSerializer):
    """Serializer para período aquisitivo de férias"""
    
    class Meta:
        model = PeriodoAquisitivo
        fields = [
            'id', 'uuid', 'colaborador', 'data_inicio', 'data_fim',
            'dias_direito', 'dias_gozados', 'dias_vendidos',
            'dias_restantes', 'status'
        ]


class SolicitacaoFeriasSerializer(serializers.ModelSerializer):
    """Serializer para solicitação de férias"""
    colaborador_nome = serializers.CharField(source='colaborador.nome_completo', read_only=True)
    
    class Meta:
        model = SolicitacaoFerias
        fields = [
            'id', 'uuid', 'colaborador', 'colaborador_nome',
            'periodo_aquisitivo', 'data_inicio', 'data_fim',
            'dias_solicitados', 'abono_pecuniario', 'dias_abono',
            'adiantamento_13', 'status', 'aprovado_por',
            'data_aprovacao', 'observacoes'
        ]
        read_only_fields = ['id', 'uuid', 'aprovado_por', 'data_aprovacao']
    
    def validate(self, data):
        """Validações customizadas"""
        if data['data_inicio'] >= data['data_fim']:
            raise serializers.ValidationError(
                'Data de início deve ser anterior à data de fim.'
            )
        
        dias = (data['data_fim'] - data['data_inicio']).days + 1
        if dias < 5:
            raise serializers.ValidationError(
                'O período mínimo de férias é de 5 dias.'
            )
        
        return data


class FeriasColetivasSerializer(serializers.ModelSerializer):
    """Serializer para férias coletivas"""
    
    class Meta:
        model = FeriasColetivas
        fields = [
            'id', 'uuid', 'titulo', 'data_inicio', 'data_fim',
            'dias', 'todos_colaboradores', 'departamentos',
            'colaboradores', 'observacoes', 'status'
        ]


class ContadorSerializer(serializers.ModelSerializer):
    """Serializer para contador"""
    
    class Meta:
        model = Contador
        fields = [
            'id', 'uuid', 'nome', 'crc', 'email',
            'telefone', 'escritorio', 'is_active'
        ]


class ExportacaoContabilSerializer(serializers.ModelSerializer):
    """Serializer para exportação contábil"""
    
    class Meta:
        model = ExportacaoContabil
        fields = [
            'id', 'uuid', 'mes', 'ano', 'tipo', 'formato',
            'arquivo', 'enviado_para', 'data_envio', 'status'
        ]
