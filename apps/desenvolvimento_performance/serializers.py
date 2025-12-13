"""
SyncRH - Desenvolvimento e Performance - Serializers
=====================================================
"""

from rest_framework import serializers
from django.utils import timezone

from .models import (
    CicloAvaliacao, AvaliacaoDesempenho, CompetenciaAvaliada,
    PDI, AcaoPDI, SyncBox, Curso, Trilha, CursoTrilha,
    MatriculaCurso, ProgressoCurso
)


class CompetenciaAvaliadaSerializer(serializers.ModelSerializer):
    """Serializer para competência avaliada"""
    
    class Meta:
        model = CompetenciaAvaliada
        fields = [
            'id', 'avaliacao', 'competencia', 'nota', 'peso',
            'evidencias', 'observacoes', 'created_at'
        ]
        read_only_fields = ['created_at']
    
    def validate_nota(self, value):
        if value < 0 or value > 5:
            raise serializers.ValidationError("A nota deve estar entre 0 e 5")
        return value


class CicloAvaliacaoSerializer(serializers.ModelSerializer):
    """Serializer para ciclo de avaliação"""
    avaliacoes_count = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = CicloAvaliacao
        fields = [
            'id', 'nome', 'ano', 'descricao', 'tipo', 'status', 'status_display',
            'data_inicio', 'data_fim', 'data_inicio_autoavaliacao', 'data_fim_autoavaliacao',
            'data_inicio_avaliacao_gestor', 'data_fim_avaliacao_gestor',
            'data_inicio_consenso', 'data_fim_consenso',
            'peso_autoavaliacao', 'peso_gestor', 'peso_pares', 'peso_subordinados',
            'avaliacoes_count', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_avaliacoes_count(self, obj):
        return obj.avaliacoes.count()
    
    def validate(self, data):
        """Valida que as datas estão em ordem"""
        if data.get('data_inicio') and data.get('data_fim'):
            if data['data_inicio'] > data['data_fim']:
                raise serializers.ValidationError(
                    "Data de início deve ser anterior à data de fim"
                )
        return data


class AvaliacaoDesempenhoListSerializer(serializers.ModelSerializer):
    """Serializer resumido para listagem de avaliações"""
    colaborador_nome = serializers.CharField(source='colaborador.nome_completo', read_only=True)
    avaliador_nome = serializers.CharField(source='avaliador.get_full_name', read_only=True)
    ciclo_nome = serializers.CharField(source='ciclo.nome', read_only=True)
    
    class Meta:
        model = AvaliacaoDesempenho
        fields = [
            'id', 'ciclo', 'ciclo_nome', 'colaborador', 'colaborador_nome',
            'avaliador', 'avaliador_nome', 'tipo', 'status', 'nota_final',
            'data_avaliacao', 'created_at'
        ]


class AvaliacaoDesempenhoDetailSerializer(serializers.ModelSerializer):
    """Serializer detalhado para avaliação"""
    colaborador_nome = serializers.CharField(source='colaborador.nome_completo', read_only=True)
    avaliador_nome = serializers.CharField(source='avaliador.get_full_name', read_only=True)
    ciclo_data = CicloAvaliacaoSerializer(source='ciclo', read_only=True)
    competencias = CompetenciaAvaliadaSerializer(many=True, read_only=True)
    
    class Meta:
        model = AvaliacaoDesempenho
        fields = [
            'id', 'ciclo', 'ciclo_data', 'colaborador', 'colaborador_nome',
            'avaliador', 'avaliador_nome', 'tipo', 'status', 'nota_final',
            'metas_atingidas', 'pontos_fortes', 'pontos_melhoria',
            'comentarios_gerais', 'feedback_colaborador', 'plano_acao',
            'competencias', 'data_avaliacao', 'data_consenso',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['nota_final', 'created_at', 'updated_at']


class AcaoPDISerializer(serializers.ModelSerializer):
    """Serializer para ação do PDI"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    dias_restantes = serializers.SerializerMethodField()
    
    class Meta:
        model = AcaoPDI
        fields = [
            'id', 'pdi', 'titulo', 'descricao', 'tipo', 'competencia',
            'prioridade', 'status', 'status_display', 'data_inicio',
            'data_previsao', 'data_conclusao', 'responsavel', 'recursos',
            'indicador_sucesso', 'progresso', 'observacoes', 'dias_restantes',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_dias_restantes(self, obj):
        if obj.data_previsao and obj.status != 'concluido':
            delta = obj.data_previsao - timezone.now().date()
            return delta.days
        return None


class PDIListSerializer(serializers.ModelSerializer):
    """Serializer resumido para listagem de PDIs"""
    colaborador_nome = serializers.CharField(source='colaborador.nome_completo', read_only=True)
    total_acoes = serializers.SerializerMethodField()
    acoes_concluidas = serializers.SerializerMethodField()
    
    class Meta:
        model = PDI
        fields = [
            'id', 'colaborador', 'colaborador_nome', 'titulo', 'status',
            'data_inicio', 'data_previsao_conclusao', 'progresso_geral',
            'total_acoes', 'acoes_concluidas', 'created_at'
        ]
    
    def get_total_acoes(self, obj):
        return obj.acoes.count()
    
    def get_acoes_concluidas(self, obj):
        return obj.acoes.filter(status='concluido').count()


class PDIDetailSerializer(serializers.ModelSerializer):
    """Serializer detalhado para PDI"""
    colaborador_nome = serializers.CharField(source='colaborador.nome_completo', read_only=True)
    gestor_nome = serializers.CharField(source='gestor.get_full_name', read_only=True)
    avaliacao_origem_data = AvaliacaoDesempenhoListSerializer(source='avaliacao_origem', read_only=True)
    acoes = AcaoPDISerializer(many=True, read_only=True)
    
    class Meta:
        model = PDI
        fields = [
            'id', 'colaborador', 'colaborador_nome', 'gestor', 'gestor_nome',
            'titulo', 'descricao', 'avaliacao_origem', 'avaliacao_origem_data',
            'status', 'data_inicio', 'data_previsao_conclusao', 'data_conclusao',
            'progresso_geral', 'objetivos', 'gap_competencias',
            'feedback_gestor', 'acoes', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['progresso_geral', 'created_at', 'updated_at']


class SyncBoxSerializer(serializers.ModelSerializer):
    """Serializer para matriz SyncBox (9Box adaptada)"""
    colaborador_nome = serializers.CharField(source='colaborador.nome_completo', read_only=True)
    quadrante_display = serializers.CharField(source='get_quadrante_display', read_only=True)
    
    class Meta:
        model = SyncBox
        fields = [
            'id', 'colaborador', 'colaborador_nome', 'ciclo', 'nota_desempenho',
            'nota_potencial', 'quadrante', 'quadrante_display', 'calibrado',
            'calibrado_por', 'data_calibracao', 'justificativa_calibracao',
            'recomendacoes', 'plano_sucessao', 'risco_perda', 'impacto_perda',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['quadrante', 'created_at', 'updated_at']


class CursoSerializer(serializers.ModelSerializer):
    """Serializer para curso"""
    matriculas_count = serializers.SerializerMethodField()
    nota_media = serializers.SerializerMethodField()
    
    class Meta:
        model = Curso
        fields = [
            'id', 'codigo', 'titulo', 'descricao', 'categoria', 'tipo',
            'modalidade', 'carga_horaria', 'conteudo_programatico',
            'objetivos', 'pre_requisitos', 'instrutor', 'fornecedor',
            'custo', 'certificado', 'validade_certificado', 'nota_minima',
            'tentativas_permitidas', 'material_url', 'video_url', 'thumbnail',
            'publicado', 'destaque', 'matriculas_count', 'nota_media',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['codigo', 'created_at', 'updated_at']
    
    def get_matriculas_count(self, obj):
        return obj.matriculas.count()
    
    def get_nota_media(self, obj):
        from django.db.models import Avg
        avg = obj.matriculas.filter(nota__isnull=False).aggregate(Avg('nota'))
        return avg['nota__avg']


class TrilhaSerializer(serializers.ModelSerializer):
    """Serializer para trilha de aprendizagem"""
    cursos_count = serializers.SerializerMethodField()
    carga_horaria_total = serializers.SerializerMethodField()
    
    class Meta:
        model = Trilha
        fields = [
            'id', 'codigo', 'nome', 'descricao', 'categoria', 'nivel',
            'publico_alvo', 'obrigatoria', 'certificado', 'thumbnail',
            'cursos_count', 'carga_horaria_total',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['codigo', 'created_at', 'updated_at']
    
    def get_cursos_count(self, obj):
        return obj.cursos_trilha.count()
    
    def get_carga_horaria_total(self, obj):
        from django.db.models import Sum
        total = obj.cursos_trilha.aggregate(
            Sum('curso__carga_horaria')
        )['curso__carga_horaria__sum']
        return total or 0


class MatriculaCursoSerializer(serializers.ModelSerializer):
    """Serializer para matrícula em curso"""
    colaborador_nome = serializers.CharField(source='colaborador.nome_completo', read_only=True)
    curso_titulo = serializers.CharField(source='curso.titulo', read_only=True)
    
    class Meta:
        model = MatriculaCurso
        fields = [
            'id', 'colaborador', 'colaborador_nome', 'curso', 'curso_titulo',
            'trilha', 'status', 'progresso', 'data_matricula', 'data_inicio',
            'data_conclusao', 'data_limite', 'nota', 'tentativas',
            'certificado_url', 'feedback', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['data_matricula', 'created_at', 'updated_at']


class ProgressoCursoSerializer(serializers.ModelSerializer):
    """Serializer para progresso em curso"""
    
    class Meta:
        model = ProgressoCurso
        fields = [
            'id', 'matricula', 'modulo', 'aula', 'status', 'progresso',
            'tempo_assistido', 'ultima_posicao', 'data_inicio', 'data_conclusao',
            'nota_quiz', 'tentativas_quiz', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
