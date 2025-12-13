"""
Admin do Módulo Desenvolvimento e Performance - SyncRH
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import (
    CicloAvaliacao, SyncBox,
    ModeloAvaliacao, CriterioAvaliacao, AvaliacaoDesempenho, RespostaAvaliacao, ConsolidacaoAvaliacao,
    PDI, MetaPDI, AcompanhamentoPDI,
    MetricaColaborador, RelatorioAnalytics,
    CategoriaCurso, Curso, ModuloCurso, AulaCurso, MatriculaCurso, ProgressoAula,
    FeedbackIA
)


# =====================================================
# CICLO E SYNCBOX
# =====================================================

@admin.register(CicloAvaliacao)
class CicloAvaliacaoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'ano', 'semestre', 'data_inicio', 'data_fim', 'status_badge']
    list_filter = ['status', 'ano']
    
    def status_badge(self, obj):
        colors = {
            'planejado': '#95a5a6',
            'autoavaliacao': '#3498db',
            'avaliacao_gestor': '#9b59b6',
            'calibracao': '#f39c12',
            'feedback': '#e67e22',
            'concluido': '#27ae60',
        }
        return format_html(
            '<span style="background:{};color:white;padding:3px 10px;border-radius:3px;">{}</span>',
            colors.get(obj.status, '#95a5a6'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(SyncBox)
class SyncBoxAdmin(admin.ModelAdmin):
    list_display = ['colaborador', 'ciclo', 'desempenho', 'potencial', 'quadrante_badge', 'classificacao']
    list_filter = ['classificacao', 'ciclo']
    search_fields = ['colaborador__nome_completo']
    
    def quadrante_badge(self, obj):
        colors = {
            9: '#27ae60', 8: '#2ecc71', 7: '#3498db',  # Alto potencial
            6: '#1abc9c', 5: '#f1c40f', 4: '#f39c12',  # Médio potencial
            3: '#e67e22', 2: '#e74c3c', 1: '#c0392b',  # Baixo potencial
        }
        return format_html(
            '<span style="background:{};color:white;padding:5px 12px;border-radius:50%;font-weight:bold;">{}</span>',
            colors.get(obj.quadrante, '#95a5a6'),
            obj.quadrante
        )
    quadrante_badge.short_description = 'Quadrante'


# =====================================================
# AVALIAÇÃO DE DESEMPENHO
# =====================================================

class CriterioAvaliacaoInline(admin.TabularInline):
    model = CriterioAvaliacao
    extra = 1


@admin.register(ModeloAvaliacao)
class ModeloAvaliacaoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'tipo', 'peso_autoavaliacao', 'peso_gestor', 'peso_pares', 'peso_subordinados']
    list_filter = ['tipo']
    inlines = [CriterioAvaliacaoInline]


class RespostaAvaliacaoInline(admin.TabularInline):
    model = RespostaAvaliacao
    extra = 0
    readonly_fields = ['criterio', 'nota', 'comentario']


@admin.register(AvaliacaoDesempenho)
class AvaliacaoDesempenhoAdmin(admin.ModelAdmin):
    list_display = ['colaborador', 'ciclo', 'tipo_avaliador', 'avaliador', 'status_badge', 'nota_final']
    list_filter = ['status', 'tipo_avaliador', 'ciclo']
    search_fields = ['colaborador__nome_completo', 'avaliador__username']
    inlines = [RespostaAvaliacaoInline]
    
    def status_badge(self, obj):
        colors = {
            'pendente': '#f39c12',
            'em_andamento': '#3498db',
            'concluida': '#27ae60',
            'validada': '#2ecc71',
        }
        return format_html(
            '<span style="background:{};color:white;padding:3px 10px;border-radius:3px;">{}</span>',
            colors.get(obj.status, '#95a5a6'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(ConsolidacaoAvaliacao)
class ConsolidacaoAvaliacaoAdmin(admin.ModelAdmin):
    list_display = ['colaborador', 'ciclo', 'nota_final_ponderada', 'classificacao_badge', 'calibrado', 'feedback_entregue']
    list_filter = ['classificacao', 'calibrado', 'feedback_entregue', 'ciclo']
    search_fields = ['colaborador__nome_completo']
    
    def classificacao_badge(self, obj):
        colors = {
            'excepcional': '#27ae60',
            'acima_esperado': '#2ecc71',
            'atende': '#3498db',
            'parcialmente': '#f39c12',
            'abaixo': '#e74c3c',
        }
        if obj.classificacao:
            return format_html(
                '<span style="background:{};color:white;padding:3px 10px;border-radius:3px;">{}</span>',
                colors.get(obj.classificacao, '#95a5a6'),
                obj.get_classificacao_display()
            )
        return '-'
    classificacao_badge.short_description = 'Classificação'


# =====================================================
# PDI
# =====================================================

class MetaPDIInline(admin.TabularInline):
    model = MetaPDI
    extra = 1


class AcompanhamentoPDIInline(admin.TabularInline):
    model = AcompanhamentoPDI
    extra = 0


@admin.register(PDI)
class PDIAdmin(admin.ModelAdmin):
    list_display = ['colaborador', 'titulo', 'data_inicio', 'data_fim', 'status_badge', 'progresso_bar', 'gerado_ia']
    list_filter = ['status', 'gerado_ia', 'ciclo']
    search_fields = ['colaborador__nome_completo', 'titulo']
    inlines = [MetaPDIInline, AcompanhamentoPDIInline]
    
    def status_badge(self, obj):
        colors = {
            'rascunho': '#95a5a6',
            'aguardando_aprovacao': '#f39c12',
            'aprovado': '#3498db',
            'em_andamento': '#9b59b6',
            'concluido': '#27ae60',
            'cancelado': '#e74c3c',
        }
        return format_html(
            '<span style="background:{};color:white;padding:3px 10px;border-radius:3px;">{}</span>',
            colors.get(obj.status, '#95a5a6'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def progresso_bar(self, obj):
        cor = '#27ae60' if obj.progresso >= 80 else '#f39c12' if obj.progresso >= 50 else '#e74c3c'
        return format_html(
            '<div style="width:100px;background:#ecf0f1;border-radius:3px;">'
            '<div style="width:{}%;background:{};height:20px;border-radius:3px;text-align:center;color:white;font-size:12px;line-height:20px;">'
            '{}%</div></div>',
            obj.progresso, cor, obj.progresso
        )
    progresso_bar.short_description = 'Progresso'


@admin.register(MetaPDI)
class MetaPDIAdmin(admin.ModelAdmin):
    list_display = ['pdi', 'titulo', 'tipo', 'prioridade', 'data_limite', 'status_badge', 'progresso']
    list_filter = ['status', 'tipo', 'prioridade']
    search_fields = ['titulo', 'pdi__colaborador__nome_completo']
    
    def status_badge(self, obj):
        colors = {
            'pendente': '#95a5a6',
            'em_andamento': '#3498db',
            'concluida': '#27ae60',
            'atrasada': '#e74c3c',
            'cancelada': '#7f8c8d',
        }
        return format_html(
            '<span style="background:{};color:white;padding:3px 10px;border-radius:3px;">{}</span>',
            colors.get(obj.status, '#95a5a6'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'


# =====================================================
# PEOPLE ANALYTICS
# =====================================================

@admin.register(MetricaColaborador)
class MetricaColaboradorAdmin(admin.ModelAdmin):
    list_display = ['colaborador', 'periodo', 'nota_desempenho', 'score_engajamento', 'risco_badge', 'treinamentos_concluidos']
    list_filter = ['risco_rotatividade', 'periodo']
    search_fields = ['colaborador__nome_completo']
    date_hierarchy = 'periodo'
    
    def risco_badge(self, obj):
        colors = {
            'baixo': '#27ae60',
            'medio': '#f39c12',
            'alto': '#e67e22',
            'critico': '#e74c3c',
        }
        if obj.risco_rotatividade:
            return format_html(
                '<span style="background:{};color:white;padding:3px 10px;border-radius:3px;">{}</span>',
                colors.get(obj.risco_rotatividade, '#95a5a6'),
                obj.get_risco_rotatividade_display()
            )
        return '-'
    risco_badge.short_description = 'Risco Rotatividade'


@admin.register(RelatorioAnalytics)
class RelatorioAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'tipo', 'periodo_inicio', 'periodo_fim', 'departamento', 'gerado_por']
    list_filter = ['tipo']
    search_fields = ['titulo']


# =====================================================
# LMS
# =====================================================

@admin.register(CategoriaCurso)
class CategoriaCursoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cor_preview', 'total_cursos']
    
    def cor_preview(self, obj):
        return format_html(
            '<span style="background:{};color:white;padding:3px 15px;border-radius:3px;">{}</span>',
            obj.cor, obj.cor
        )
    cor_preview.short_description = 'Cor'
    
    def total_cursos(self, obj):
        return obj.cursos.count()
    total_cursos.short_description = 'Cursos'


class ModuloCursoInline(admin.TabularInline):
    model = ModuloCurso
    extra = 1


@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'codigo', 'categoria', 'nivel', 'carga_horaria', 'status_badge', 'estatisticas']
    list_filter = ['status', 'nivel', 'categoria', 'obrigatorio']
    search_fields = ['titulo', 'codigo']
    filter_horizontal = ['departamentos_obrigatorios', 'cargos_obrigatorios']
    inlines = [ModuloCursoInline]
    
    def status_badge(self, obj):
        colors = {
            'rascunho': '#95a5a6',
            'publicado': '#27ae60',
            'arquivado': '#7f8c8d',
        }
        return format_html(
            '<span style="background:{};color:white;padding:3px 10px;border-radius:3px;">{}</span>',
            colors.get(obj.status, '#95a5a6'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def estatisticas(self, obj):
        taxa = (obj.total_conclusoes / obj.total_matriculas * 100) if obj.total_matriculas > 0 else 0
        return format_html(
            '<span title="Matrículas: {} | Conclusões: {} | Taxa: {:.0f}%">📊 {}/{} ({:.0f}%)</span>',
            obj.total_matriculas, obj.total_conclusoes, taxa,
            obj.total_conclusoes, obj.total_matriculas, taxa
        )
    estatisticas.short_description = 'Conclusões'


class AulaCursoInline(admin.TabularInline):
    model = AulaCurso
    extra = 1


@admin.register(ModuloCurso)
class ModuloCursoAdmin(admin.ModelAdmin):
    list_display = ['curso', 'titulo', 'ordem', 'total_aulas']
    list_filter = ['curso']
    inlines = [AulaCursoInline]
    
    def total_aulas(self, obj):
        return obj.aulas.count()
    total_aulas.short_description = 'Aulas'


@admin.register(MatriculaCurso)
class MatriculaCursoAdmin(admin.ModelAdmin):
    list_display = ['colaborador', 'curso', 'status_badge', 'progresso_bar', 'nota_final', 'certificado_emitido']
    list_filter = ['status', 'aprovado', 'certificado_emitido']
    search_fields = ['colaborador__nome_completo', 'curso__titulo']
    
    def status_badge(self, obj):
        colors = {
            'matriculado': '#3498db',
            'em_andamento': '#9b59b6',
            'concluido': '#27ae60',
            'reprovado': '#e74c3c',
            'cancelado': '#7f8c8d',
            'expirado': '#95a5a6',
        }
        return format_html(
            '<span style="background:{};color:white;padding:3px 10px;border-radius:3px;">{}</span>',
            colors.get(obj.status, '#95a5a6'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def progresso_bar(self, obj):
        cor = '#27ae60' if obj.progresso >= 80 else '#f39c12' if obj.progresso >= 50 else '#3498db'
        return format_html(
            '<div style="width:80px;background:#ecf0f1;border-radius:3px;">'
            '<div style="width:{}%;background:{};height:18px;border-radius:3px;text-align:center;color:white;font-size:11px;line-height:18px;">'
            '{}%</div></div>',
            obj.progresso, cor, obj.progresso
        )
    progresso_bar.short_description = 'Progresso'


# =====================================================
# IA
# =====================================================

@admin.register(FeedbackIA)
class FeedbackIAAdmin(admin.ModelAdmin):
    list_display = ['tipo', 'colaborador', 'utilizado', 'avaliacao_usuario', 'solicitado_por', 'created_at']
    list_filter = ['tipo', 'utilizado']
    search_fields = ['conteudo', 'colaborador__nome_completo']
    readonly_fields = ['conteudo', 'contexto']
