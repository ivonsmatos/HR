"""
SyncRH - Gestão Comportamental - Serializers
============================================
"""

from rest_framework import serializers

from .models import (
    QuestionarioProfiler, QuestaoProfiler, OpcaoResposta,
    AplicacaoProfiler, RespostaProfiler, PerfilDISC,
    PerfilIdealCargo, MatchComportamental, ComparacaoTime
)


class OpcaoRespostaSerializer(serializers.ModelSerializer):
    """Serializer para opção de resposta"""
    
    class Meta:
        model = OpcaoResposta
        fields = ['id', 'texto', 'ordem']


class QuestaoProfilerSerializer(serializers.ModelSerializer):
    """Serializer para questão do profiler"""
    opcoes = OpcaoRespostaSerializer(many=True, read_only=True)
    
    class Meta:
        model = QuestaoProfiler
        fields = [
            'id', 'questionario', 'numero', 'texto', 'instrucao',
            'tipo', 'obrigatoria', 'opcoes', 'is_active'
        ]


class QuestionarioProfilerListSerializer(serializers.ModelSerializer):
    """Serializer resumido para listagem de questionários"""
    total_questoes = serializers.SerializerMethodField()
    
    class Meta:
        model = QuestionarioProfiler
        fields = [
            'id', 'titulo', 'tipo', 'versao', 'tempo_estimado',
            'publicado', 'total_questoes', 'created_at'
        ]
    
    def get_total_questoes(self, obj):
        return obj.questoes.count()


class QuestionarioProfilerDetailSerializer(serializers.ModelSerializer):
    """Serializer detalhado para questionário"""
    questoes = QuestaoProfilerSerializer(many=True, read_only=True)
    
    class Meta:
        model = QuestionarioProfiler
        fields = [
            'id', 'titulo', 'descricao', 'instrucoes', 'tipo', 'versao',
            'tempo_estimado', 'publicado', 'questoes',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class RespostaProfilerSerializer(serializers.ModelSerializer):
    """Serializer para resposta do profiler"""
    
    class Meta:
        model = RespostaProfiler
        fields = [
            'id', 'aplicacao', 'questao', 'opcao_mais', 'opcao_menos',
            'tempo_resposta', 'created_at'
        ]
        read_only_fields = ['created_at']


class PerfilDISCSerializer(serializers.ModelSerializer):
    """Serializer para perfil DISC"""
    perfil_grafico = serializers.SerializerMethodField()
    
    class Meta:
        model = PerfilDISC
        fields = [
            'id', 'aplicacao', 'tipo_perfil', 'dominancia', 'influencia',
            'estabilidade', 'conformidade', 'perfil_principal', 'padrao',
            'intensidade', 'perfil_grafico', 'descricao_perfil',
            'pontos_fortes', 'areas_desenvolvimento', 'estilo_comunicacao',
            'ambiente_ideal', 'fatores_motivacao', 'fatores_estresse',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_perfil_grafico(self, obj):
        """Retorna dados para renderizar gráfico DISC"""
        return {
            'labels': ['Dominância', 'Influência', 'Estabilidade', 'Conformidade'],
            'valores': [
                float(obj.dominancia),
                float(obj.influencia),
                float(obj.estabilidade),
                float(obj.conformidade)
            ],
            'cores': ['#e53935', '#fdd835', '#43a047', '#1e88e5']
        }


class AplicacaoProfilerListSerializer(serializers.ModelSerializer):
    """Serializer resumido para listagem de aplicações"""
    colaborador_nome = serializers.CharField(source='colaborador.nome_completo', read_only=True)
    questionario_titulo = serializers.CharField(source='questionario.titulo', read_only=True)
    
    class Meta:
        model = AplicacaoProfiler
        fields = [
            'id', 'colaborador', 'colaborador_nome', 'questionario',
            'questionario_titulo', 'status', 'data_inicio', 'data_conclusao',
            'created_at'
        ]


class AplicacaoProfilerDetailSerializer(serializers.ModelSerializer):
    """Serializer detalhado para aplicação"""
    colaborador_nome = serializers.CharField(source='colaborador.nome_completo', read_only=True)
    questionario_data = QuestionarioProfilerListSerializer(source='questionario', read_only=True)
    perfil_disc = PerfilDISCSerializer(read_only=True)
    respostas = RespostaProfilerSerializer(many=True, read_only=True)
    
    class Meta:
        model = AplicacaoProfiler
        fields = [
            'id', 'colaborador', 'colaborador_nome', 'questionario',
            'questionario_data', 'status', 'contexto', 'data_inicio',
            'data_conclusao', 'tempo_total', 'ip_resposta',
            'perfil_disc', 'respostas', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class PerfilIdealCargoSerializer(serializers.ModelSerializer):
    """Serializer para perfil ideal de cargo"""
    cargo_nome = serializers.CharField(source='cargo.titulo', read_only=True)
    perfil_grafico = serializers.SerializerMethodField()
    
    class Meta:
        model = PerfilIdealCargo
        fields = [
            'id', 'cargo', 'cargo_nome', 'dominancia_min', 'dominancia_max',
            'influencia_min', 'influencia_max', 'estabilidade_min', 'estabilidade_max',
            'conformidade_min', 'conformidade_max', 'perfil_ideal', 'tolerancia',
            'justificativa', 'competencias_comportamentais', 'perfil_grafico',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_perfil_grafico(self, obj):
        """Retorna dados para renderizar gráfico do perfil ideal"""
        return {
            'labels': ['D', 'I', 'S', 'C'],
            'min': [
                float(obj.dominancia_min),
                float(obj.influencia_min),
                float(obj.estabilidade_min),
                float(obj.conformidade_min)
            ],
            'max': [
                float(obj.dominancia_max),
                float(obj.influencia_max),
                float(obj.estabilidade_max),
                float(obj.conformidade_max)
            ],
            'ideal': [
                (float(obj.dominancia_min) + float(obj.dominancia_max)) / 2,
                (float(obj.influencia_min) + float(obj.influencia_max)) / 2,
                (float(obj.estabilidade_min) + float(obj.estabilidade_max)) / 2,
                (float(obj.conformidade_min) + float(obj.conformidade_max)) / 2
            ]
        }


class MatchComportamentalSerializer(serializers.ModelSerializer):
    """Serializer para match comportamental"""
    colaborador_nome = serializers.SerializerMethodField()
    cargo_nome = serializers.SerializerMethodField()
    classificacao_display = serializers.CharField(source='get_classificacao_display', read_only=True)
    
    class Meta:
        model = MatchComportamental
        fields = [
            'id', 'perfil_disc', 'perfil_ideal', 'colaborador_nome', 'cargo_nome',
            'match_dominancia', 'match_influencia', 'match_estabilidade',
            'match_conformidade', 'match_geral', 'classificacao', 'classificacao_display',
            'gaps_identificados', 'recomendacoes', 'adequacao_funcao',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_colaborador_nome(self, obj):
        if obj.perfil_disc and obj.perfil_disc.aplicacao:
            return obj.perfil_disc.aplicacao.colaborador.nome_completo
        return None
    
    def get_cargo_nome(self, obj):
        if obj.perfil_ideal:
            return obj.perfil_ideal.cargo.titulo
        return None


class ComparacaoTimeSerializer(serializers.ModelSerializer):
    """Serializer para comparação de time"""
    departamento_nome = serializers.CharField(source='departamento.nome', read_only=True)
    criado_por_nome = serializers.CharField(source='criado_por.get_full_name', read_only=True)
    total_colaboradores = serializers.SerializerMethodField()
    
    class Meta:
        model = ComparacaoTime
        fields = [
            'id', 'nome', 'departamento', 'departamento_nome', 'colaboradores',
            'total_colaboradores', 'mapa_time', 'distribuicao_disc',
            'gaps_identificados', 'pontos_fortes_time', 'pontos_atencao_time',
            'recomendacoes_composicao', 'criado_por', 'criado_por_nome',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_total_colaboradores(self, obj):
        return obj.colaboradores.count() if obj.colaboradores else 0
