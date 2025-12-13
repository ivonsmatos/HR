"""
Admin do Módulo Engajamento e Retenção - SyncRH
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import (
    # Pesquisa de Clima
    PesquisaClima, DimensaoClima, PerguntaClima, RespostaClima, PlanoAcaoClima,
    # eNPS
    PesquisaeNPS, RespostaeNPS,
    # Rotatividade
    AnaliseRotatividade, AnaliseDemissional,
    # Cargos e Salários
    TabelaSalarial, FaixaSalarial, PlanoCarreira, SolicitacaoPromocao,
    # Benefícios
    TipoBeneficio, BeneficioColaborador,
    # SuperApp
    NotificacaoColaborador, Reconhecimento, FeedbackRapido,
    # IA
    InsightEngajamento,
)


# =====================================================
# INLINES
# =====================================================

class DimensaoClimaInline(admin.TabularInline):
    model = DimensaoClima
    extra = 1
    fields = ['nome', 'peso', 'ordem', 'score_medio']
    readonly_fields = ['score_medio']


class PerguntaClimaInline(admin.TabularInline):
    model = PerguntaClima
    extra = 1
    fields = ['texto', 'tipo', 'obrigatoria', 'ordem']


class FaixaSalarialInline(admin.TabularInline):
    model = FaixaSalarial
    extra = 1
    fields = ['cargo', 'salario_minimo', 'salario_medio', 'salario_maximo']


# =====================================================
# PESQUISA DE CLIMA
# =====================================================

@admin.register(PesquisaClima)
class PesquisaClimaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'status_badge', 'data_inicio', 'data_fim', 'taxa_participacao_display', 'score_geral_display', 'is_active']
    list_filter = ['status', 'is_active', 'data_inicio']
    search_fields = ['titulo', 'descricao']
    inlines = [DimensaoClimaInline]
    readonly_fields = ['taxa_participacao', 'score_geral', 'uuid', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('titulo', 'descricao', 'status')
        }),
        ('Período', {
            'fields': ('data_inicio', 'data_fim')
        }),
        ('Configurações', {
            'fields': ('anonima', 'obrigatoria', 'todos_colaboradores')
        }),
        ('Resultados', {
            'fields': ('taxa_participacao', 'score_geral'),
            'classes': ('collapse',)
        }),
        ('Sistema', {
            'fields': ('criado_por', 'is_active', 'uuid', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        colors = {
            'rascunho': '#6c757d',
            'agendada': '#17a2b8',
            'em_andamento': '#ffc107',
            'encerrada': '#6c757d',
            'analisada': '#28a745',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html('<span style="background:{}; color:white; padding:3px 10px; border-radius:10px;">{}</span>', color, obj.get_status_display())
    status_badge.short_description = 'Status'
    
    def taxa_participacao_display(self, obj):
        if obj.taxa_participacao:
            color = '#28a745' if obj.taxa_participacao >= 70 else '#ffc107' if obj.taxa_participacao >= 50 else '#dc3545'
            return format_html('<span style="color:{}; font-weight:bold;">{}%</span>', color, obj.taxa_participacao)
        return '-'
    taxa_participacao_display.short_description = 'Participação'
    
    def score_geral_display(self, obj):
        if obj.score_geral:
            return format_html('<span style="font-weight:bold;">{}/5</span>', obj.score_geral)
        return '-'
    score_geral_display.short_description = 'Score'


@admin.register(DimensaoClima)
class DimensaoClimaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'pesquisa', 'peso', 'ordem', 'score_medio']
    list_filter = ['pesquisa']
    search_fields = ['nome', 'pesquisa__titulo']
    inlines = [PerguntaClimaInline]


@admin.register(PerguntaClima)
class PerguntaClimaAdmin(admin.ModelAdmin):
    list_display = ['texto_resumido', 'dimensao', 'tipo', 'obrigatoria', 'media_respostas']
    list_filter = ['tipo', 'obrigatoria', 'dimensao__pesquisa']
    search_fields = ['texto']
    
    def texto_resumido(self, obj):
        return obj.texto[:50] + '...' if len(obj.texto) > 50 else obj.texto
    texto_resumido.short_description = 'Pergunta'


@admin.register(RespostaClima)
class RespostaClimaAdmin(admin.ModelAdmin):
    list_display = ['pesquisa', 'data_resposta', 'tempo_preenchimento_display']
    list_filter = ['pesquisa', 'data_resposta']
    readonly_fields = ['data_resposta', 'tempo_preenchimento']
    
    def tempo_preenchimento_display(self, obj):
        mins = obj.tempo_preenchimento // 60
        secs = obj.tempo_preenchimento % 60
        return f'{mins}m {secs}s'
    tempo_preenchimento_display.short_description = 'Tempo'


@admin.register(PlanoAcaoClima)
class PlanoAcaoClimaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'pesquisa', 'responsavel', 'status_badge', 'progresso_bar', 'data_fim']
    list_filter = ['status', 'sugerido_ia', 'pesquisa']
    search_fields = ['titulo', 'descricao']
    
    def status_badge(self, obj):
        colors = {
            'planejado': '#17a2b8',
            'em_andamento': '#ffc107',
            'concluido': '#28a745',
            'cancelado': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html('<span style="background:{}; color:white; padding:3px 10px; border-radius:10px;">{}</span>', color, obj.get_status_display())
    status_badge.short_description = 'Status'
    
    def progresso_bar(self, obj):
        color = '#28a745' if obj.progresso >= 75 else '#ffc107' if obj.progresso >= 50 else '#dc3545'
        return format_html(
            '<div style="width:100px; background:#e9ecef; border-radius:4px;">'
            '<div style="width:{}%; background:{}; height:20px; border-radius:4px; text-align:center; color:white; font-size:12px; line-height:20px;">{}</div>'
            '</div>',
            obj.progresso, color, f'{obj.progresso}%'
        )
    progresso_bar.short_description = 'Progresso'


# =====================================================
# eNPS
# =====================================================

@admin.register(PesquisaeNPS)
class PesquisaeNPSAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'status_badge', 'data_inicio', 'data_fim', 'total_respostas', 'enps_badge']
    list_filter = ['status', 'data_inicio']
    search_fields = ['titulo']
    readonly_fields = ['total_respostas', 'promotores', 'neutros', 'detratores', 'score_enps']
    
    fieldsets = (
        ('Informações', {
            'fields': ('titulo', 'descricao', 'status')
        }),
        ('Período', {
            'fields': ('data_inicio', 'data_fim')
        }),
        ('Perguntas', {
            'fields': ('pergunta_principal', 'perguntas_abertas')
        }),
        ('Resultados', {
            'fields': ('total_respostas', 'promotores', 'neutros', 'detratores', 'score_enps'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        colors = {
            'rascunho': '#6c757d',
            'em_andamento': '#ffc107',
            'encerrada': '#28a745',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html('<span style="background:{}; color:white; padding:3px 10px; border-radius:10px;">{}</span>', color, obj.get_status_display())
    status_badge.short_description = 'Status'
    
    def enps_badge(self, obj):
        if obj.score_enps is None:
            return '-'
        if obj.score_enps >= 50:
            color = '#28a745'
            label = 'Excelente'
        elif obj.score_enps >= 0:
            color = '#ffc107'
            label = 'Bom'
        else:
            color = '#dc3545'
            label = 'Crítico'
        return format_html('<span style="background:{}; color:white; padding:3px 10px; border-radius:10px;">{} ({})</span>', color, obj.score_enps, label)
    enps_badge.short_description = 'eNPS'


@admin.register(RespostaeNPS)
class RespostaeNPSAdmin(admin.ModelAdmin):
    list_display = ['pesquisa', 'nota', 'classificacao_badge', 'data_resposta']
    list_filter = ['classificacao', 'pesquisa']
    search_fields = ['comentarios']
    readonly_fields = ['classificacao', 'data_resposta']
    
    def classificacao_badge(self, obj):
        colors = {
            'promotor': '#28a745',
            'neutro': '#ffc107',
            'detrator': '#dc3545',
        }
        color = colors.get(obj.classificacao, '#6c757d')
        return format_html('<span style="background:{}; color:white; padding:3px 10px; border-radius:10px;">{}</span>', color, obj.get_classificacao_display())
    classificacao_badge.short_description = 'Classificação'


# =====================================================
# ROTATIVIDADE
# =====================================================

@admin.register(AnaliseRotatividade)
class AnaliseRotatividadeAdmin(admin.ModelAdmin):
    list_display = ['colaborador', 'data_analise', 'score_risco_display', 'classificacao_badge', 'tendencia_display']
    list_filter = ['classificacao', 'tendencia', 'data_analise']
    search_fields = ['colaborador__nome_completo']
    readonly_fields = ['score_anterior', 'tendencia', 'data_analise']
    
    def score_risco_display(self, obj):
        color = '#dc3545' if obj.score_risco >= 75 else '#ffc107' if obj.score_risco >= 50 else '#17a2b8' if obj.score_risco >= 25 else '#28a745'
        return format_html(
            '<div style="width:60px; background:#e9ecef; border-radius:4px;">'
            '<div style="width:{}%; background:{}; height:20px; border-radius:4px;"></div>'
            '</div><span style="color:{}; font-weight:bold;"> {}</span>',
            obj.score_risco, color, color, obj.score_risco
        )
    score_risco_display.short_description = 'Score'
    
    def classificacao_badge(self, obj):
        colors = {
            'baixo': '#28a745',
            'medio': '#17a2b8',
            'alto': '#ffc107',
            'critico': '#dc3545',
        }
        emojis = {
            'baixo': '✅',
            'medio': '⚠️',
            'alto': '🔶',
            'critico': '🚨',
        }
        color = colors.get(obj.classificacao, '#6c757d')
        emoji = emojis.get(obj.classificacao, '')
        return format_html('<span style="background:{}; color:white; padding:3px 10px; border-radius:10px;">{} {}</span>', color, emoji, obj.get_classificacao_display())
    classificacao_badge.short_description = 'Risco'
    
    def tendencia_display(self, obj):
        if not obj.tendencia:
            return '-'
        icons = {
            'subindo': ('↑', '#dc3545'),
            'estavel': ('→', '#6c757d'),
            'descendo': ('↓', '#28a745'),
        }
        icon, color = icons.get(obj.tendencia, ('?', '#6c757d'))
        return format_html('<span style="color:{}; font-size:18px; font-weight:bold;">{}</span>', color, icon)
    tendencia_display.short_description = 'Tendência'


@admin.register(AnaliseDemissional)
class AnaliseDemissionalAdmin(admin.ModelAdmin):
    list_display = ['colaborador', 'data_demissao', 'tipo_badge', 'motivo_principal', 'entrevista_realizada', 'nota_experiencia']
    list_filter = ['tipo', 'motivo_principal', 'entrevista_realizada', 'data_demissao']
    search_fields = ['colaborador__nome_completo', 'motivos_detalhados']
    
    fieldsets = (
        ('Colaborador', {
            'fields': ('colaborador', 'data_demissao', 'tipo')
        }),
        ('Motivos', {
            'fields': ('motivo_principal', 'motivos_detalhados')
        }),
        ('Entrevista Demissional', {
            'fields': ('entrevista_realizada', 'data_entrevista', 'entrevistador')
        }),
        ('Feedback', {
            'fields': ('recomendaria_empresa', 'voltaria_empresa', 'nota_experiencia')
        }),
        ('Pontos', {
            'fields': ('pontos_positivos', 'pontos_negativos', 'sugestoes_melhoria'),
            'classes': ('collapse',)
        }),
        ('IA', {
            'fields': ('insights_ia',),
            'classes': ('collapse',)
        }),
    )
    
    def tipo_badge(self, obj):
        colors = {
            'voluntaria': '#ffc107',
            'involuntaria': '#dc3545',
            'acordo': '#17a2b8',
            'termino_contrato': '#6c757d',
            'aposentadoria': '#28a745',
        }
        color = colors.get(obj.tipo, '#6c757d')
        return format_html('<span style="background:{}; color:white; padding:3px 10px; border-radius:10px;">{}</span>', color, obj.get_tipo_display())
    tipo_badge.short_description = 'Tipo'


# =====================================================
# CARGOS E SALÁRIOS
# =====================================================

@admin.register(TabelaSalarial)
class TabelaSalarialAdmin(admin.ModelAdmin):
    list_display = ['nome', 'data_vigencia', 'total_faixas', 'is_active']
    list_filter = ['is_active', 'data_vigencia']
    search_fields = ['nome', 'descricao']
    inlines = [FaixaSalarialInline]
    
    def total_faixas(self, obj):
        return obj.faixas.count()
    total_faixas.short_description = 'Faixas'


@admin.register(FaixaSalarial)
class FaixaSalarialAdmin(admin.ModelAdmin):
    list_display = ['cargo', 'tabela', 'salario_range']
    list_filter = ['tabela']
    search_fields = ['cargo__nome']
    
    def salario_range(self, obj):
        return f'R$ {obj.salario_minimo:,.2f} - R$ {obj.salario_maximo:,.2f}'
    salario_range.short_description = 'Faixa Salarial'


@admin.register(PlanoCarreira)
class PlanoCarreiraAdmin(admin.ModelAdmin):
    list_display = ['nome', 'total_cargos', 'is_active']
    list_filter = ['is_active']
    search_fields = ['nome', 'descricao']
    
    def total_cargos(self, obj):
        return len(obj.trilha) if obj.trilha else 0
    total_cargos.short_description = 'Cargos na Trilha'


@admin.register(SolicitacaoPromocao)
class SolicitacaoPromocaoAdmin(admin.ModelAdmin):
    list_display = ['colaborador', 'tipo_badge', 'cargo_atual', 'cargo_proposto', 'aumento_display', 'status_badge']
    list_filter = ['tipo', 'status', 'created_at']
    search_fields = ['colaborador__nome_completo', 'justificativa']
    readonly_fields = ['percentual_aumento', 'uuid', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Colaborador', {
            'fields': ('colaborador', 'tipo', 'status')
        }),
        ('Cargos', {
            'fields': ('cargo_atual', 'cargo_proposto')
        }),
        ('Valores', {
            'fields': ('salario_atual', 'salario_proposto', 'percentual_aumento')
        }),
        ('Justificativa', {
            'fields': ('justificativa',)
        }),
        ('Aprovação', {
            'fields': ('solicitado_por', 'data_efetivacao'),
            'classes': ('collapse',)
        }),
        ('Sistema', {
            'fields': ('is_active', 'uuid', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def tipo_badge(self, obj):
        colors = {
            'promocao': '#28a745',
            'merito': '#17a2b8',
            'enquadramento': '#6c757d',
            'reajuste': '#ffc107',
        }
        color = colors.get(obj.tipo, '#6c757d')
        return format_html('<span style="background:{}; color:white; padding:3px 10px; border-radius:10px;">{}</span>', color, obj.get_tipo_display())
    tipo_badge.short_description = 'Tipo'
    
    def aumento_display(self, obj):
        if obj.salario_atual and obj.salario_proposto:
            pct = ((obj.salario_proposto - obj.salario_atual) / obj.salario_atual) * 100
            color = '#28a745' if pct > 0 else '#dc3545' if pct < 0 else '#6c757d'
            return format_html('<span style="color:{}; font-weight:bold;">+{:.1f}%</span>', color, pct)
        return '-'
    aumento_display.short_description = 'Aumento'
    
    def status_badge(self, obj):
        colors = {
            'rascunho': '#6c757d',
            'pendente_gestor': '#ffc107',
            'aprovado_gestor': '#17a2b8',
            'pendente_rh': '#ffc107',
            'aprovado_rh': '#17a2b8',
            'pendente_diretoria': '#ffc107',
            'aprovado': '#28a745',
            'rejeitado': '#dc3545',
            'efetivado': '#28a745',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html('<span style="background:{}; color:white; padding:3px 10px; border-radius:10px;">{}</span>', color, obj.get_status_display())
    status_badge.short_description = 'Status'


# =====================================================
# BENEFÍCIOS
# =====================================================

@admin.register(TipoBeneficio)
class TipoBeneficioAdmin(admin.ModelAdmin):
    list_display = ['nome', 'categoria_badge', 'valor_padrao_display', 'elegibilidade', 'obrigatorio', 'flexivel', 'is_active']
    list_filter = ['categoria', 'elegibilidade', 'obrigatorio', 'flexivel', 'is_active']
    search_fields = ['nome', 'descricao', 'fornecedor']
    
    def categoria_badge(self, obj):
        colors = {
            'alimentacao': '#28a745',
            'transporte': '#17a2b8',
            'saude': '#dc3545',
            'educacao': '#6f42c1',
            'bem_estar': '#e83e8c',
            'financeiro': '#fd7e14',
            'outros': '#6c757d',
        }
        color = colors.get(obj.categoria, '#6c757d')
        return format_html('<span style="background:{}; color:white; padding:3px 10px; border-radius:10px;">{}</span>', color, obj.get_categoria_display())
    categoria_badge.short_description = 'Categoria'
    
    def valor_padrao_display(self, obj):
        if obj.valor_padrao:
            return f'R$ {obj.valor_padrao:,.2f}'
        return '-'
    valor_padrao_display.short_description = 'Valor Padrão'


@admin.register(BeneficioColaborador)
class BeneficioColaboradorAdmin(admin.ModelAdmin):
    list_display = ['colaborador', 'tipo_beneficio', 'valor_display', 'desconto_display', 'data_inicio', 'status_badge']
    list_filter = ['tipo_beneficio', 'status', 'data_inicio']
    search_fields = ['colaborador__nome_completo', 'tipo_beneficio__nome']
    
    def valor_display(self, obj):
        return f'R$ {obj.valor:,.2f}'
    valor_display.short_description = 'Valor'
    
    def desconto_display(self, obj):
        if obj.valor_desconto:
            return f'R$ {obj.valor_desconto:,.2f}'
        return '-'
    desconto_display.short_description = 'Desconto'
    
    def status_badge(self, obj):
        colors = {
            'ativo': '#28a745',
            'suspenso': '#ffc107',
            'cancelado': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html('<span style="background:{}; color:white; padding:3px 10px; border-radius:10px;">{}</span>', color, obj.get_status_display())
    status_badge.short_description = 'Status'


# =====================================================
# SUPERAPP
# =====================================================

@admin.register(NotificacaoColaborador)
class NotificacaoColaboradorAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'colaborador', 'tipo_badge', 'lida', 'created_at']
    list_filter = ['tipo', 'lida', 'created_at']
    search_fields = ['titulo', 'mensagem', 'colaborador__nome_completo']
    readonly_fields = ['data_leitura', 'created_at']
    
    def tipo_badge(self, obj):
        colors = {
            'info': '#17a2b8',
            'alerta': '#ffc107',
            'urgente': '#dc3545',
            'lembrete': '#6c757d',
            'parabens': '#28a745',
            'feedback': '#6f42c1',
            'ponto': '#fd7e14',
            'ferias': '#20c997',
            'treinamento': '#e83e8c',
            'pesquisa': '#007bff',
        }
        color = colors.get(obj.tipo, '#6c757d')
        return format_html('<span style="background:{}; color:white; padding:3px 10px; border-radius:10px;">{}</span>', color, obj.get_tipo_display())
    tipo_badge.short_description = 'Tipo'


@admin.register(Reconhecimento)
class ReconhecimentoAdmin(admin.ModelAdmin):
    list_display = ['de_colaborador', 'para_colaborador', 'tipo_badge', 'publico', 'pontos', 'created_at']
    list_filter = ['tipo', 'publico', 'created_at']
    search_fields = ['de_colaborador__nome_completo', 'para_colaborador__nome_completo', 'mensagem']
    readonly_fields = ['created_at']
    
    def tipo_badge(self, obj):
        emojis = {
            'obrigado': '🙏',
            'parabens': '🎉',
            'inspiracao': '💡',
            'trabalho_equipe': '🤝',
            'inovacao': '🚀',
            'lideranca': '👑',
            'ajuda': '🆘',
        }
        emoji = emojis.get(obj.tipo, '⭐')
        return format_html('<span style="background:#f8f9fa; padding:3px 10px; border-radius:10px;">{} {}</span>', emoji, obj.get_tipo_display())
    tipo_badge.short_description = 'Tipo'


@admin.register(FeedbackRapido)
class FeedbackRapidoAdmin(admin.ModelAdmin):
    list_display = ['de_colaborador', 'para_colaborador', 'tipo_badge', 'privado', 'visualizado', 'created_at']
    list_filter = ['tipo', 'privado', 'visualizado', 'created_at']
    search_fields = ['de_colaborador__nome_completo', 'para_colaborador__nome_completo', 'conteudo']
    readonly_fields = ['data_visualizacao', 'created_at']
    
    def tipo_badge(self, obj):
        colors = {
            'positivo': '#28a745',
            'construtivo': '#ffc107',
            'solicitado': '#17a2b8',
        }
        color = colors.get(obj.tipo, '#6c757d')
        return format_html('<span style="background:{}; color:white; padding:3px 10px; border-radius:10px;">{}</span>', color, obj.get_tipo_display())
    tipo_badge.short_description = 'Tipo'


# =====================================================
# IA
# =====================================================

@admin.register(InsightEngajamento)
class InsightEngajamentoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'tipo_badge', 'prioridade_badge', 'departamento', 'acao_tomada', 'created_at']
    list_filter = ['tipo', 'prioridade', 'acao_tomada', 'created_at']
    search_fields = ['titulo', 'descricao', 'acao_sugerida']
    readonly_fields = ['created_at', 'updated_at']
    
    def tipo_badge(self, obj):
        colors = {
            'clima': '#17a2b8',
            'enps': '#28a745',
            'rotatividade': '#dc3545',
            'engajamento': '#6f42c1',
            'padrao': '#fd7e14',
            'acao_sugerida': '#e83e8c',
        }
        color = colors.get(obj.tipo, '#6c757d')
        return format_html('<span style="background:{}; color:white; padding:3px 10px; border-radius:10px;">{}</span>', color, obj.get_tipo_display())
    tipo_badge.short_description = 'Tipo'
    
    def prioridade_badge(self, obj):
        colors = {
            'baixa': '#28a745',
            'media': '#17a2b8',
            'alta': '#ffc107',
            'critica': '#dc3545',
        }
        emojis = {
            'baixa': '🟢',
            'media': '🔵',
            'alta': '🟠',
            'critica': '🔴',
        }
        color = colors.get(obj.prioridade, '#6c757d')
        emoji = emojis.get(obj.prioridade, '')
        return format_html('<span style="color:{};">{} {}</span>', color, emoji, obj.get_prioridade_display())
    prioridade_badge.short_description = 'Prioridade'
