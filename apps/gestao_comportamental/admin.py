"""
Admin do Módulo Gestão Comportamental - SyncRH
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import (
    # Profiler
    QuestionarioProfiler, QuestaoProfiler, AplicacaoProfiler, RespostaProfiler, PerfilDISC,
    # Engenharia de Cargos
    PerfilIdealCargo, CompetenciaComportamental,
    # Matcher
    MatchComportamental,
    # Métricas
    MetricaProfiler, ComparacaoTime,
    # Histórico
    HistoricoPerfilColaborador,
    # IA
    InsightComportamental,
)


# =====================================================
# INLINES
# =====================================================

class QuestaoProfilerInline(admin.TabularInline):
    model = QuestaoProfiler
    extra = 1
    fields = ['ordem', 'tipo', 'texto']
    ordering = ['ordem']


class RespostaProfilerInline(admin.TabularInline):
    model = RespostaProfiler
    extra = 0
    readonly_fields = ['questao', 'resposta', 'tempo_resposta']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


# =====================================================
# PROFILER
# =====================================================

@admin.register(QuestionarioProfiler)
class QuestionarioProfilerAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'tipo_badge', 'versao', 'total_questoes', 'tempo_estimado', 'publicado_badge']
    list_filter = ['tipo', 'publicado', 'created_at']
    search_fields = ['titulo', 'descricao']
    inlines = [QuestaoProfilerInline]
    readonly_fields = ['uuid', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Informações', {
            'fields': ('titulo', 'descricao', 'tipo', 'versao')
        }),
        ('Configurações', {
            'fields': ('tempo_estimado', 'total_questoes', 'instrucoes')
        }),
        ('Publicação', {
            'fields': ('publicado', 'data_publicacao')
        }),
        ('Sistema', {
            'fields': ('is_active', 'uuid', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def tipo_badge(self, obj):
        colors = {
            'disc': '#007bff',
            'disc_extendido': '#6f42c1',
            'big5': '#28a745',
            'mbti': '#fd7e14',
            'personalizado': '#6c757d',
        }
        color = colors.get(obj.tipo, '#6c757d')
        return format_html('<span style="background:{}; color:white; padding:3px 10px; border-radius:10px;">{}</span>', color, obj.get_tipo_display())
    tipo_badge.short_description = 'Tipo'
    
    def publicado_badge(self, obj):
        if obj.publicado:
            return format_html('<span style="color:#28a745; font-weight:bold;">✓ Publicado</span>')
        return format_html('<span style="color:#6c757d;">Rascunho</span>')
    publicado_badge.short_description = 'Status'


@admin.register(QuestaoProfiler)
class QuestaoProfilerAdmin(admin.ModelAdmin):
    list_display = ['ordem', 'questionario', 'tipo', 'texto_resumido']
    list_filter = ['tipo', 'questionario']
    search_fields = ['texto']
    ordering = ['questionario', 'ordem']
    
    def texto_resumido(self, obj):
        if obj.texto:
            return obj.texto[:50] + '...' if len(obj.texto) > 50 else obj.texto
        return '-'
    texto_resumido.short_description = 'Texto'


@admin.register(AplicacaoProfiler)
class AplicacaoProfilerAdmin(admin.ModelAdmin):
    list_display = ['get_pessoa', 'questionario', 'status_badge', 'data_envio', 'data_conclusao', 'tempo_display']
    list_filter = ['status', 'questionario', 'data_envio']
    search_fields = ['colaborador__nome_completo', 'candidato__nome']
    inlines = [RespostaProfilerInline]
    readonly_fields = ['data_envio', 'data_inicio', 'data_conclusao', 'tempo_total', 'token_acesso', 'uuid']
    
    def get_pessoa(self, obj):
        if obj.colaborador:
            return format_html('<span title="Colaborador">👤 {}</span>', obj.colaborador.nome_completo)
        elif obj.candidato:
            return format_html('<span title="Candidato">🎯 {}</span>', obj.candidato.nome)
        return '-'
    get_pessoa.short_description = 'Pessoa'
    
    def status_badge(self, obj):
        colors = {
            'pendente': '#ffc107',
            'em_andamento': '#17a2b8',
            'concluido': '#28a745',
            'expirado': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html('<span style="background:{}; color:white; padding:3px 10px; border-radius:10px;">{}</span>', color, obj.get_status_display())
    status_badge.short_description = 'Status'
    
    def tempo_display(self, obj):
        if obj.tempo_total:
            mins = obj.tempo_total // 60
            secs = obj.tempo_total % 60
            return f'{mins}m {secs}s'
        return '-'
    tempo_display.short_description = 'Tempo'


@admin.register(PerfilDISC)
class PerfilDISCAdmin(admin.ModelAdmin):
    list_display = ['get_pessoa', 'perfil_principal_badge', 'disc_visual', 'padrao', 'indice_consistencia_display', 'tipo_perfil']
    list_filter = ['tipo_perfil', 'perfil_principal', 'padrao']
    search_fields = ['aplicacao__colaborador__nome_completo', 'aplicacao__candidato__nome']
    readonly_fields = ['perfil_principal', 'indice_consistencia', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Perfil', {
            'fields': ('aplicacao', 'tipo_perfil', 'perfil_principal', 'padrao')
        }),
        ('Scores DISC', {
            'fields': ('dominancia', 'influencia', 'estabilidade', 'conformidade')
        }),
        ('Características', {
            'fields': ('pontos_fortes', 'areas_desenvolvimento', 'estilo_comunicacao', 'estilo_lideranca'),
            'classes': ('collapse',)
        }),
        ('Motivação', {
            'fields': ('ambiente_ideal', 'fatores_motivacao', 'fatores_desmotivacao'),
            'classes': ('collapse',)
        }),
        ('Qualidade', {
            'fields': ('indice_consistencia',)
        }),
    )
    
    def get_pessoa(self, obj):
        if obj.aplicacao.colaborador:
            return obj.aplicacao.colaborador.nome_completo
        elif obj.aplicacao.candidato:
            return obj.aplicacao.candidato.nome
        return '-'
    get_pessoa.short_description = 'Pessoa'
    
    def perfil_principal_badge(self, obj):
        colors = {
            'D': '#dc3545',
            'I': '#ffc107',
            'S': '#28a745',
            'C': '#007bff',
        }
        letra = obj.perfil_principal[0] if obj.perfil_principal else '?'
        color = colors.get(letra, '#6c757d')
        return format_html(
            '<span style="background:{}; color:white; padding:5px 12px; border-radius:50%; font-weight:bold; font-size:14px;">{}</span>',
            color, obj.perfil_principal
        )
    perfil_principal_badge.short_description = 'Perfil'
    
    def disc_visual(self, obj):
        return format_html(
            '<div style="display:flex; gap:5px;">'
            '<span style="background:#dc3545; color:white; padding:2px 8px; border-radius:4px;" title="Dominância">D:{}</span>'
            '<span style="background:#ffc107; color:black; padding:2px 8px; border-radius:4px;" title="Influência">I:{}</span>'
            '<span style="background:#28a745; color:white; padding:2px 8px; border-radius:4px;" title="Estabilidade">S:{}</span>'
            '<span style="background:#007bff; color:white; padding:2px 8px; border-radius:4px;" title="Conformidade">C:{}</span>'
            '</div>',
            obj.dominancia, obj.influencia, obj.estabilidade, obj.conformidade
        )
    disc_visual.short_description = 'DISC'
    
    def indice_consistencia_display(self, obj):
        color = '#28a745' if obj.indice_consistencia >= 70 else '#ffc107' if obj.indice_consistencia >= 50 else '#dc3545'
        return format_html('<span style="color:{}; font-weight:bold;">{}%</span>', color, obj.indice_consistencia)
    indice_consistencia_display.short_description = 'Consistência'


# =====================================================
# ENGENHARIA DE CARGOS
# =====================================================

@admin.register(PerfilIdealCargo)
class PerfilIdealCargoAdmin(admin.ModelAdmin):
    list_display = ['cargo', 'disc_ideal_visual', 'pesos_display', 'definido_por', 'data_definicao']
    list_filter = ['cargo__departamento', 'created_at']
    search_fields = ['cargo__nome', 'descricao_perfil']
    
    fieldsets = (
        ('Cargo', {
            'fields': ('cargo', 'descricao_perfil')
        }),
        ('Dominância (D)', {
            'fields': (('dominancia_min', 'dominancia_ideal', 'dominancia_max'), 'peso_dominancia'),
            'classes': ('collapse',)
        }),
        ('Influência (I)', {
            'fields': (('influencia_min', 'influencia_ideal', 'influencia_max'), 'peso_influencia'),
            'classes': ('collapse',)
        }),
        ('Estabilidade (S)', {
            'fields': (('estabilidade_min', 'estabilidade_ideal', 'estabilidade_max'), 'peso_estabilidade'),
            'classes': ('collapse',)
        }),
        ('Conformidade (C)', {
            'fields': (('conformidade_min', 'conformidade_ideal', 'conformidade_max'), 'peso_conformidade'),
            'classes': ('collapse',)
        }),
        ('Competências', {
            'fields': ('competencias',)
        }),
        ('Definição', {
            'fields': ('definido_por', 'data_definicao'),
            'classes': ('collapse',)
        }),
    )
    
    def disc_ideal_visual(self, obj):
        return format_html(
            '<div style="display:flex; gap:5px; font-size:11px;">'
            '<span style="background:#dc3545; color:white; padding:2px 6px; border-radius:4px;" title="D: {}-{}-{}">D:{}</span>'
            '<span style="background:#ffc107; color:black; padding:2px 6px; border-radius:4px;" title="I: {}-{}-{}">I:{}</span>'
            '<span style="background:#28a745; color:white; padding:2px 6px; border-radius:4px;" title="S: {}-{}-{}">S:{}</span>'
            '<span style="background:#007bff; color:white; padding:2px 6px; border-radius:4px;" title="C: {}-{}-{}">C:{}</span>'
            '</div>',
            obj.dominancia_min, obj.dominancia_ideal, obj.dominancia_max, obj.dominancia_ideal,
            obj.influencia_min, obj.influencia_ideal, obj.influencia_max, obj.influencia_ideal,
            obj.estabilidade_min, obj.estabilidade_ideal, obj.estabilidade_max, obj.estabilidade_ideal,
            obj.conformidade_min, obj.conformidade_ideal, obj.conformidade_max, obj.conformidade_ideal,
        )
    disc_ideal_visual.short_description = 'DISC Ideal'
    
    def pesos_display(self, obj):
        return format_html(
            '<span style="font-size:11px;">D:{}% I:{}% S:{}% C:{}%</span>',
            obj.peso_dominancia, obj.peso_influencia, obj.peso_estabilidade, obj.peso_conformidade
        )
    pesos_display.short_description = 'Pesos'


@admin.register(CompetenciaComportamental)
class CompetenciaComportamentalAdmin(admin.ModelAdmin):
    list_display = ['nome', 'categoria_badge', 'disc_badge', 'is_active']
    list_filter = ['categoria', 'disc_relacionado', 'is_active']
    search_fields = ['nome', 'descricao']
    
    def categoria_badge(self, obj):
        colors = {
            'lideranca': '#dc3545',
            'comunicacao': '#ffc107',
            'relacionamento': '#28a745',
            'execucao': '#007bff',
            'analise': '#6f42c1',
            'adaptabilidade': '#fd7e14',
            'inovacao': '#e83e8c',
            'organizacao': '#20c997',
        }
        color = colors.get(obj.categoria, '#6c757d')
        return format_html('<span style="background:{}; color:white; padding:3px 10px; border-radius:10px;">{}</span>', color, obj.get_categoria_display())
    categoria_badge.short_description = 'Categoria'
    
    def disc_badge(self, obj):
        if not obj.disc_relacionado:
            return '-'
        colors = {
            'D': '#dc3545',
            'I': '#ffc107',
            'S': '#28a745',
            'C': '#007bff',
        }
        letra = obj.disc_relacionado[0]
        color = colors.get(letra, '#6c757d')
        return format_html('<span style="background:{}; color:white; padding:2px 8px; border-radius:4px;">{}</span>', color, obj.disc_relacionado)
    disc_badge.short_description = 'DISC'


# =====================================================
# MATCHER
# =====================================================

@admin.register(MatchComportamental)
class MatchComportamentalAdmin(admin.ModelAdmin):
    list_display = ['get_pessoa', 'get_cargo', 'match_geral_display', 'classificacao_badge', 'match_visual', 'created_at']
    list_filter = ['classificacao', 'created_at']
    search_fields = ['perfil_disc__aplicacao__colaborador__nome_completo', 'perfil_ideal__cargo__nome']
    readonly_fields = ['match_dominancia', 'match_influencia', 'match_estabilidade', 'match_conformidade', 'match_geral', 'classificacao']
    
    fieldsets = (
        ('Match', {
            'fields': ('perfil_disc', 'perfil_ideal', 'match_geral', 'classificacao')
        }),
        ('Detalhes por Dimensão', {
            'fields': ('match_dominancia', 'match_influencia', 'match_estabilidade', 'match_conformidade'),
            'classes': ('collapse',)
        }),
        ('Análise', {
            'fields': ('pontos_alinhamento', 'pontos_atencao', 'recomendacoes'),
            'classes': ('collapse',)
        }),
        ('IA', {
            'fields': ('analise_ia',),
            'classes': ('collapse',)
        }),
    )
    
    def get_pessoa(self, obj):
        if obj.perfil_disc.aplicacao.colaborador:
            return obj.perfil_disc.aplicacao.colaborador.nome_completo
        elif obj.perfil_disc.aplicacao.candidato:
            return obj.perfil_disc.aplicacao.candidato.nome
        return '-'
    get_pessoa.short_description = 'Pessoa'
    
    def get_cargo(self, obj):
        return obj.perfil_ideal.cargo.nome
    get_cargo.short_description = 'Cargo'
    
    def match_geral_display(self, obj):
        color = '#28a745' if obj.match_geral >= 75 else '#ffc107' if obj.match_geral >= 50 else '#dc3545'
        return format_html(
            '<div style="width:60px; background:#e9ecef; border-radius:4px;">'
            '<div style="width:{}%; background:{}; height:20px; border-radius:4px; text-align:center; color:white; font-size:11px; line-height:20px;">{}%</div>'
            '</div>',
            min(obj.match_geral, 100), color, f'{obj.match_geral:.0f}'
        )
    match_geral_display.short_description = 'Match'
    
    def classificacao_badge(self, obj):
        colors = {
            'excelente': '#28a745',
            'muito_bom': '#17a2b8',
            'bom': '#ffc107',
            'razoavel': '#fd7e14',
            'baixo': '#dc3545',
        }
        emojis = {
            'excelente': '⭐',
            'muito_bom': '✨',
            'bom': '👍',
            'razoavel': '⚠️',
            'baixo': '❌',
        }
        color = colors.get(obj.classificacao, '#6c757d')
        emoji = emojis.get(obj.classificacao, '')
        return format_html('<span style="background:{}; color:white; padding:3px 10px; border-radius:10px;">{} {}</span>', color, emoji, obj.get_classificacao_display())
    classificacao_badge.short_description = 'Classificação'
    
    def match_visual(self, obj):
        def bar(val, color):
            return f'<div style="width:{val}%; background:{color}; height:8px; border-radius:2px;"></div>'
        
        return format_html(
            '<div style="width:100px; display:flex; flex-direction:column; gap:2px;" title="D:{}% I:{}% S:{}% C:{}%">'
            '<div style="width:100%; background:#f8f9fa; border-radius:2px;">{}</div>'
            '<div style="width:100%; background:#f8f9fa; border-radius:2px;">{}</div>'
            '<div style="width:100%; background:#f8f9fa; border-radius:2px;">{}</div>'
            '<div style="width:100%; background:#f8f9fa; border-radius:2px;">{}</div>'
            '</div>',
            obj.match_dominancia, obj.match_influencia, obj.match_estabilidade, obj.match_conformidade,
            format_html(bar(min(obj.match_dominancia, 100), '#dc3545')),
            format_html(bar(min(obj.match_influencia, 100), '#ffc107')),
            format_html(bar(min(obj.match_estabilidade, 100), '#28a745')),
            format_html(bar(min(obj.match_conformidade, 100), '#007bff')),
        )
    match_visual.short_description = 'DISC'


# =====================================================
# MÉTRICAS
# =====================================================

@admin.register(MetricaProfiler)
class MetricaProfilerAdmin(admin.ModelAdmin):
    list_display = ['data_referencia', 'get_escopo', 'total_aplicacoes', 'total_concluidos', 'taxa_conclusao_display', 'media_match_display']
    list_filter = ['data_referencia', 'departamento', 'cargo']
    date_hierarchy = 'data_referencia'
    
    def get_escopo(self, obj):
        if obj.departamento:
            return f"Depto: {obj.departamento.nome}"
        elif obj.cargo:
            return f"Cargo: {obj.cargo.nome}"
        return "Geral"
    get_escopo.short_description = 'Escopo'
    
    def taxa_conclusao_display(self, obj):
        color = '#28a745' if obj.taxa_conclusao >= 80 else '#ffc107' if obj.taxa_conclusao >= 60 else '#dc3545'
        return format_html('<span style="color:{}; font-weight:bold;">{}%</span>', color, obj.taxa_conclusao)
    taxa_conclusao_display.short_description = 'Taxa Conclusão'
    
    def media_match_display(self, obj):
        if obj.media_match:
            color = '#28a745' if obj.media_match >= 70 else '#ffc107' if obj.media_match >= 50 else '#dc3545'
            return format_html('<span style="color:{}; font-weight:bold;">{}%</span>', color, obj.media_match)
        return '-'
    media_match_display.short_description = 'Match Médio'


@admin.register(ComparacaoTime)
class ComparacaoTimeAdmin(admin.ModelAdmin):
    list_display = ['nome', 'departamento', 'total_perfis', 'criado_por', 'created_at']
    list_filter = ['departamento', 'created_at']
    search_fields = ['nome', 'descricao']
    filter_horizontal = ['perfis']
    
    def total_perfis(self, obj):
        return obj.perfis.count()
    total_perfis.short_description = 'Perfis'


# =====================================================
# HISTÓRICO
# =====================================================

@admin.register(HistoricoPerfilColaborador)
class HistoricoPerfilColaboradorAdmin(admin.ModelAdmin):
    list_display = ['colaborador', 'contexto_badge', 'get_perfil', 'variacao_display', 'created_at']
    list_filter = ['contexto', 'created_at']
    search_fields = ['colaborador__nome_completo']
    
    def contexto_badge(self, obj):
        colors = {
            'admissao': '#28a745',
            'promocao': '#007bff',
            'periodico': '#6c757d',
            'transferencia': '#fd7e14',
            'desenvolvimento': '#6f42c1',
            'outro': '#6c757d',
        }
        color = colors.get(obj.contexto, '#6c757d')
        return format_html('<span style="background:{}; color:white; padding:3px 10px; border-radius:10px;">{}</span>', color, obj.get_contexto_display())
    contexto_badge.short_description = 'Contexto'
    
    def get_perfil(self, obj):
        return obj.perfil_disc.perfil_principal
    get_perfil.short_description = 'Perfil'
    
    def variacao_display(self, obj):
        def var_icon(val):
            if val > 0:
                return f'<span style="color:#28a745;">+{val}</span>'
            elif val < 0:
                return f'<span style="color:#dc3545;">{val}</span>'
            return f'<span style="color:#6c757d;">0</span>'
        
        return format_html(
            'D:{} I:{} S:{} C:{}',
            format_html(var_icon(obj.variacao_dominancia)),
            format_html(var_icon(obj.variacao_influencia)),
            format_html(var_icon(obj.variacao_estabilidade)),
            format_html(var_icon(obj.variacao_conformidade)),
        )
    variacao_display.short_description = 'Variação'


# =====================================================
# IA
# =====================================================

@admin.register(InsightComportamental)
class InsightComportamentalAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'tipo_badge', 'prioridade_badge', 'get_escopo', 'acao_tomada', 'created_at']
    list_filter = ['tipo', 'prioridade', 'acao_tomada', 'created_at']
    search_fields = ['titulo', 'descricao']
    
    def tipo_badge(self, obj):
        colors = {
            'compatibilidade': '#007bff',
            'desenvolvimento': '#28a745',
            'time': '#6f42c1',
            'lideranca': '#dc3545',
            'comunicacao': '#ffc107',
            'conflito': '#fd7e14',
            'padrao': '#17a2b8',
        }
        color = colors.get(obj.tipo, '#6c757d')
        return format_html('<span style="background:{}; color:white; padding:3px 10px; border-radius:10px;">{}</span>', color, obj.get_tipo_display())
    tipo_badge.short_description = 'Tipo'
    
    def prioridade_badge(self, obj):
        colors = {
            'baixa': '#28a745',
            'media': '#ffc107',
            'alta': '#dc3545',
        }
        emojis = {
            'baixa': '🟢',
            'media': '🟡',
            'alta': '🔴',
        }
        color = colors.get(obj.prioridade, '#6c757d')
        emoji = emojis.get(obj.prioridade, '')
        return format_html('<span style="color:{};">{} {}</span>', color, emoji, obj.get_prioridade_display())
    prioridade_badge.short_description = 'Prioridade'
    
    def get_escopo(self, obj):
        if obj.colaborador:
            return f"👤 {obj.colaborador.nome_completo}"
        elif obj.departamento:
            return f"🏢 {obj.departamento.nome}"
        return "Geral"
    get_escopo.short_description = 'Escopo'
