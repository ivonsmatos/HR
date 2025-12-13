"""
SyncRH - Engajamento e Retenção - Serializers
=============================================
"""

from rest_framework import serializers
from django.utils import timezone

from .models import (
    PesquisaClima, PerguntaClima, RespostaClima, ResultadoClima,
    PesquisaeNPS, RespostaeNPS, TipoBeneficio, BeneficioColaborador,
    SolicitacaoPromocao, Reconhecimento, BadgeReconhecimento,
    AlertaRotatividade, NotificacaoColaborador
)


class PerguntaClimaSerializer(serializers.ModelSerializer):
    """Serializer para pergunta de clima"""
    
    class Meta:
        model = PerguntaClima
        fields = [
            'id', 'pesquisa', 'categoria', 'texto', 'tipo_resposta',
            'obrigatoria', 'ordem', 'opcoes', 'is_active'
        ]


class RespostaClimaSerializer(serializers.ModelSerializer):
    """Serializer para resposta de clima"""
    
    class Meta:
        model = RespostaClima
        fields = [
            'id', 'pergunta', 'nota', 'texto_resposta', 'created_at'
        ]
        read_only_fields = ['created_at']


class ResultadoClimaSerializer(serializers.ModelSerializer):
    """Serializer para resultado de clima"""
    
    class Meta:
        model = ResultadoClima
        fields = [
            'id', 'pesquisa', 'departamento', 'categoria', 'media_nota',
            'total_respostas', 'percentual_participacao', 'desvio_padrao',
            'detalhamento', 'is_active'
        ]


class PesquisaClimaListSerializer(serializers.ModelSerializer):
    """Serializer resumido para listagem de pesquisas de clima"""
    participacao = serializers.SerializerMethodField()
    
    class Meta:
        model = PesquisaClima
        fields = [
            'id', 'titulo', 'ano', 'status', 'data_inicio', 'data_fim',
            'anonima', 'participacao', 'created_at'
        ]
    
    def get_participacao(self, obj):
        total_respostas = obj.resultados.aggregate(
            total=serializers.Sum('total_respostas')
        ).get('total', 0) or 0
        return total_respostas


class PesquisaClimaDetailSerializer(serializers.ModelSerializer):
    """Serializer detalhado para pesquisa de clima"""
    perguntas = PerguntaClimaSerializer(many=True, read_only=True)
    resultados = ResultadoClimaSerializer(many=True, read_only=True)
    
    class Meta:
        model = PesquisaClima
        fields = [
            'id', 'titulo', 'descricao', 'ano', 'status', 'data_inicio',
            'data_fim', 'anonima', 'publico_alvo', 'departamentos',
            'perguntas', 'resultados', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class RespostaeNPSSerializer(serializers.ModelSerializer):
    """Serializer para resposta eNPS"""
    classificacao = serializers.SerializerMethodField()
    
    class Meta:
        model = RespostaeNPS
        fields = [
            'id', 'pesquisa', 'nota', 'classificacao', 'motivo',
            'sugestao', 'data_resposta'
        ]
        read_only_fields = ['data_resposta']
    
    def get_classificacao(self, obj):
        if obj.nota >= 9:
            return 'promotor'
        elif obj.nota >= 7:
            return 'neutro'
        return 'detrator'


class PesquisaeNPSSerializer(serializers.ModelSerializer):
    """Serializer para pesquisa eNPS"""
    estatisticas = serializers.SerializerMethodField()
    
    class Meta:
        model = PesquisaeNPS
        fields = [
            'id', 'titulo', 'descricao', 'status', 'data_inicio', 'data_fim',
            'pergunta_principal', 'pergunta_motivo', 'anonima',
            'estatisticas', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_estatisticas(self, obj):
        respostas = obj.respostas.all()
        total = respostas.count()
        
        if total == 0:
            return {
                'total_respostas': 0,
                'promotores': 0,
                'neutros': 0,
                'detratores': 0,
                'enps_score': None
            }
        
        promotores = respostas.filter(nota__gte=9).count()
        detratores = respostas.filter(nota__lte=6).count()
        neutros = total - promotores - detratores
        
        enps = ((promotores - detratores) / total) * 100
        
        return {
            'total_respostas': total,
            'promotores': promotores,
            'neutros': neutros,
            'detratores': detratores,
            'enps_score': round(enps, 1)
        }


class TipoBeneficioSerializer(serializers.ModelSerializer):
    """Serializer para tipo de benefício"""
    
    class Meta:
        model = TipoBeneficio
        fields = [
            'id', 'nome', 'descricao', 'categoria', 'tipo_valor',
            'valor_padrao', 'periodicidade', 'elegibilidade',
            'documentacao_necessaria', 'fornecedor', 'is_active'
        ]


class BeneficioColaboradorSerializer(serializers.ModelSerializer):
    """Serializer para benefício do colaborador"""
    tipo_beneficio_data = TipoBeneficioSerializer(source='tipo_beneficio', read_only=True)
    colaborador_nome = serializers.CharField(source='colaborador.nome_completo', read_only=True)
    
    class Meta:
        model = BeneficioColaborador
        fields = [
            'id', 'colaborador', 'colaborador_nome', 'tipo_beneficio',
            'tipo_beneficio_data', 'status', 'valor', 'data_inicio',
            'data_fim', 'dependentes_inclusos', 'detalhes', 'observacoes',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class SolicitacaoPromocaoSerializer(serializers.ModelSerializer):
    """Serializer para solicitação de promoção"""
    colaborador_nome = serializers.CharField(source='colaborador.nome_completo', read_only=True)
    solicitante_nome = serializers.CharField(source='solicitante.get_full_name', read_only=True)
    cargo_atual_nome = serializers.CharField(source='cargo_atual.titulo', read_only=True)
    cargo_proposto_nome = serializers.CharField(source='cargo_proposto.titulo', read_only=True)
    
    class Meta:
        model = SolicitacaoPromocao
        fields = [
            'id', 'colaborador', 'colaborador_nome', 'solicitante', 'solicitante_nome',
            'tipo', 'cargo_atual', 'cargo_atual_nome', 'cargo_proposto', 'cargo_proposto_nome',
            'salario_atual', 'salario_proposto', 'percentual_aumento',
            'justificativa', 'evidencias', 'status', 'aprovador', 'data_aprovacao',
            'parecer_aprovador', 'data_efetivacao',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['percentual_aumento', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Calcula percentual de aumento"""
        if data.get('salario_atual') and data.get('salario_proposto'):
            atual = float(data['salario_atual'])
            proposto = float(data['salario_proposto'])
            if atual > 0:
                data['percentual_aumento'] = ((proposto - atual) / atual) * 100
        return data


class BadgeReconhecimentoSerializer(serializers.ModelSerializer):
    """Serializer para badge de reconhecimento"""
    
    class Meta:
        model = BadgeReconhecimento
        fields = [
            'id', 'nome', 'descricao', 'icone', 'cor', 'pontos',
            'criterio_conquista', 'is_active'
        ]


class ReconhecimentoSerializer(serializers.ModelSerializer):
    """Serializer para reconhecimento"""
    colaborador_nome = serializers.CharField(source='colaborador.nome_completo', read_only=True)
    reconhecido_por_nome = serializers.CharField(source='reconhecido_por.get_full_name', read_only=True)
    badge_data = BadgeReconhecimentoSerializer(source='badge', read_only=True)
    
    class Meta:
        model = Reconhecimento
        fields = [
            'id', 'colaborador', 'colaborador_nome', 'reconhecido_por',
            'reconhecido_por_nome', 'tipo', 'categoria', 'titulo', 'descricao',
            'badge', 'badge_data', 'pontos', 'visibilidade', 'data_reconhecimento',
            'curtidas', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['curtidas', 'created_at', 'updated_at']


class AlertaRotatividadeSerializer(serializers.ModelSerializer):
    """Serializer para alerta de rotatividade"""
    colaborador_nome = serializers.CharField(source='colaborador.nome_completo', read_only=True)
    
    class Meta:
        model = AlertaRotatividade
        fields = [
            'id', 'colaborador', 'colaborador_nome', 'nivel_risco',
            'probabilidade_saida', 'fatores_risco', 'indicadores',
            'recomendacoes', 'status', 'responsavel', 'data_deteccao',
            'acoes_tomadas', 'resultado', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class NotificacaoColaboradorSerializer(serializers.ModelSerializer):
    """Serializer para notificação do colaborador"""
    
    class Meta:
        model = NotificacaoColaborador
        fields = [
            'id', 'colaborador', 'tipo', 'titulo', 'mensagem', 'link',
            'icone', 'lida', 'data_leitura', 'importante', 'expira_em',
            'is_active', 'created_at'
        ]
        read_only_fields = ['created_at']
