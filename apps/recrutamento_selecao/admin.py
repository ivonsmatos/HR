"""
Admin do Módulo Recrutamento e Seleção - SyncRH
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import (
    PerfilCargo, CompetenciaCargo,
    PerfilComportamental, MatchPerfil,
    Candidato, ExperienciaProfissional,
    Vaga, CandidaturaVaga, Entrevista,
    MetricaRecrutamento,
    PaginaCarreiras, DepoimentoColaborador,
    SugestaoIA
)


# =====================================================
# ENGENHARIA DE CARGOS
# =====================================================

class CompetenciaCargoInline(admin.TabularInline):
    model = CompetenciaCargo
    extra = 1


@admin.register(PerfilCargo)
class PerfilCargoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'codigo', 'disc_preview', 'escolaridade_minima', 'experiencia_minima', 'is_template']
    list_filter = ['is_template', 'escolaridade_minima']
    search_fields = ['nome', 'codigo']
    inlines = [CompetenciaCargoInline]
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'codigo', 'descricao', 'is_template')
        }),
        ('Perfil DISC', {
            'fields': ('dominancia', 'influencia', 'estabilidade', 'conformidade'),
            'description': 'Defina o perfil comportamental ideal (0-100)'
        }),
        ('Competências', {
            'fields': ('competencias_tecnicas', 'competencias_comportamentais')
        }),
        ('Requisitos', {
            'fields': ('escolaridade_minima', 'experiencia_minima', 'idiomas')
        }),
    )
    
    def disc_preview(self, obj):
        return format_html(
            '<span style="color:#e74c3c;">D:{}</span> '
            '<span style="color:#f1c40f;">I:{}</span> '
            '<span style="color:#27ae60;">S:{}</span> '
            '<span style="color:#3498db;">C:{}</span>',
            obj.dominancia, obj.influencia, obj.estabilidade, obj.conformidade
        )
    disc_preview.short_description = 'DISC'


# =====================================================
# PROFILER
# =====================================================

@admin.register(PerfilComportamental)
class PerfilComportamentalAdmin(admin.ModelAdmin):
    list_display = ['pessoa_nome', 'perfil_dominante', 'disc_preview', 'preenchido', 'data_mapeamento']
    list_filter = ['perfil_dominante', 'preenchido']
    search_fields = ['candidato__nome', 'colaborador__nome_completo']
    readonly_fields = ['token_preenchimento', 'data_preenchimento']
    
    fieldsets = (
        ('Pessoa', {
            'fields': ('candidato', 'colaborador')
        }),
        ('Perfil DISC', {
            'fields': ('dominancia', 'influencia', 'estabilidade', 'conformidade', 'perfil_dominante')
        }),
        ('Análise Detalhada', {
            'fields': ('pontos_fortes', 'areas_desenvolvimento', 'estilo_comunicacao', 'estilo_lideranca', 'ambiente_ideal'),
            'classes': ('collapse',)
        }),
        ('Fatores', {
            'fields': ('fatores_motivacionais', 'fatores_estresse'),
            'classes': ('collapse',)
        }),
        ('Preenchimento', {
            'fields': ('token_preenchimento', 'preenchido', 'data_preenchimento'),
            'classes': ('collapse',)
        }),
    )
    
    def pessoa_nome(self, obj):
        if obj.candidato:
            return obj.candidato.nome
        elif obj.colaborador:
            return obj.colaborador.nome_completo
        return '-'
    pessoa_nome.short_description = 'Pessoa'
    
    def disc_preview(self, obj):
        return format_html(
            '<span style="color:#e74c3c;">D:{}</span> '
            '<span style="color:#f1c40f;">I:{}</span> '
            '<span style="color:#27ae60;">S:{}</span> '
            '<span style="color:#3498db;">C:{}</span>',
            obj.dominancia, obj.influencia, obj.estabilidade, obj.conformidade
        )
    disc_preview.short_description = 'DISC'


# =====================================================
# MATCHER
# =====================================================

@admin.register(MatchPerfil)
class MatchPerfilAdmin(admin.ModelAdmin):
    list_display = ['perfil_comportamental', 'perfil_cargo', 'aderencia_badge', 'recomendacao_badge']
    list_filter = ['recomendacao']
    
    def aderencia_badge(self, obj):
        cor = '#27ae60' if obj.aderencia_geral >= 80 else '#f39c12' if obj.aderencia_geral >= 60 else '#e74c3c'
        return format_html(
            '<span style="background:{};color:white;padding:3px 10px;border-radius:3px;">{}%</span>',
            cor, obj.aderencia_geral
        )
    aderencia_badge.short_description = 'Aderência'
    
    def recomendacao_badge(self, obj):
        colors = {
            'altamente_recomendado': '#27ae60',
            'recomendado': '#3498db',
            'potencial': '#f39c12',
            'nao_recomendado': '#e74c3c',
        }
        if obj.recomendacao:
            return format_html(
                '<span style="background:{};color:white;padding:3px 10px;border-radius:3px;">{}</span>',
                colors.get(obj.recomendacao, '#95a5a6'),
                obj.get_recomendacao_display()
            )
        return '-'
    recomendacao_badge.short_description = 'Recomendação'


# =====================================================
# BANCO DE TALENTOS
# =====================================================

class ExperienciaProfissionalInline(admin.TabularInline):
    model = ExperienciaProfissional
    extra = 0


@admin.register(Candidato)
class CandidatoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'email', 'area_atuacao', 'anos_experiencia', 'escolaridade', 'estrelas_display', 'origem']
    list_filter = ['escolaridade', 'origem', 'favorito', 'blacklist', 'aceita_remoto']
    search_fields = ['nome', 'email', 'cpf', 'curriculo_texto', 'habilidades']
    inlines = [ExperienciaProfissionalInline]
    
    fieldsets = (
        ('Dados Pessoais', {
            'fields': ('nome', 'email', 'telefone', 'cpf', 'data_nascimento', 'foto')
        }),
        ('Localização', {
            'fields': ('cidade', 'estado', 'pais')
        }),
        ('Currículo', {
            'fields': ('curriculo', 'linkedin', 'portfolio')
        }),
        ('Formação', {
            'fields': ('escolaridade', 'area_formacao', 'instituicao')
        }),
        ('Experiência', {
            'fields': ('anos_experiencia', 'area_atuacao', 'cargo_atual', 'empresa_atual')
        }),
        ('Skills', {
            'fields': ('habilidades', 'idiomas', 'certificacoes', 'palavras_chave')
        }),
        ('Preferências', {
            'fields': ('pretensao_salarial', 'disponibilidade', 'aceita_remoto', 'aceita_hibrido', 'aceita_presencial')
        }),
        ('Classificação', {
            'fields': ('origem', 'tags', 'estrelas', 'favorito')
        }),
        ('Blacklist', {
            'fields': ('blacklist', 'motivo_blacklist'),
            'classes': ('collapse',)
        }),
    )
    
    def estrelas_display(self, obj):
        return '⭐' * obj.estrelas if obj.estrelas else '-'
    estrelas_display.short_description = 'Estrelas'


# =====================================================
# VAGAS
# =====================================================

class CandidaturaVagaInline(admin.TabularInline):
    model = CandidaturaVaga
    extra = 0
    readonly_fields = ['candidato', 'status', 'match_score', 'created_at']
    can_delete = False


@admin.register(Vaga)
class VagaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'codigo', 'modalidade', 'status_badge', 'candidaturas_count', 'recrutador', 'data_abertura']
    list_filter = ['status', 'modalidade', 'tipo_contrato', 'publicar_site_carreiras']
    search_fields = ['titulo', 'codigo', 'descricao']
    inlines = [CandidaturaVagaInline]
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('titulo', 'codigo', 'perfil_cargo', 'status')
        }),
        ('Descrição', {
            'fields': ('descricao', 'responsabilidades', 'requisitos', 'beneficios')
        }),
        ('Detalhes', {
            'fields': ('tipo_contrato', 'modalidade', 'cidade', 'estado', 'quantidade_vagas')
        }),
        ('Salário', {
            'fields': ('faixa_salarial_min', 'faixa_salarial_max', 'exibir_salario')
        }),
        ('Datas', {
            'fields': ('data_limite',)
        }),
        ('Responsáveis', {
            'fields': ('recrutador', 'gestor_vaga')
        }),
        ('Publicação', {
            'fields': ('publicar_site_carreiras', 'publicar_linkedin')
        }),
        ('Processo Seletivo', {
            'fields': ('etapas',),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        colors = {
            'rascunho': '#95a5a6',
            'aberta': '#27ae60',
            'em_processo': '#3498db',
            'pausada': '#f39c12',
            'fechada': '#7f8c8d',
            'cancelada': '#e74c3c',
        }
        return format_html(
            '<span style="background:{};color:white;padding:3px 10px;border-radius:3px;">{}</span>',
            colors.get(obj.status, '#95a5a6'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def candidaturas_count(self, obj):
        return obj.candidaturas.count()
    candidaturas_count.short_description = 'Candidaturas'


# =====================================================
# CANDIDATURAS
# =====================================================

class EntrevistaInline(admin.TabularInline):
    model = Entrevista
    extra = 0


@admin.register(CandidaturaVaga)
class CandidaturaVagaAdmin(admin.ModelAdmin):
    list_display = ['candidato', 'vaga', 'etapa_atual', 'status_badge', 'match_badge', 'nota_final']
    list_filter = ['status', 'etapa_atual']
    search_fields = ['candidato__nome', 'vaga__titulo']
    inlines = [EntrevistaInline]
    
    def status_badge(self, obj):
        colors = {
            'inscrito': '#95a5a6',
            'em_triagem': '#f39c12',
            'aprovado_triagem': '#3498db',
            'reprovado_triagem': '#e74c3c',
            'entrevista_agendada': '#9b59b6',
            'entrevista_realizada': '#1abc9c',
            'teste_pendente': '#e67e22',
            'teste_realizado': '#16a085',
            'aprovado': '#27ae60',
            'reprovado': '#c0392b',
            'desistiu': '#7f8c8d',
            'contratado': '#2ecc71',
        }
        return format_html(
            '<span style="background:{};color:white;padding:3px 10px;border-radius:3px;">{}</span>',
            colors.get(obj.status, '#95a5a6'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def match_badge(self, obj):
        if obj.match_score:
            cor = '#27ae60' if obj.match_score >= 80 else '#f39c12' if obj.match_score >= 60 else '#e74c3c'
            return format_html(
                '<span style="background:{};color:white;padding:3px 10px;border-radius:3px;">{}%</span>',
                cor, obj.match_score
            )
        return '-'
    match_badge.short_description = 'Match'


@admin.register(Entrevista)
class EntrevistaAdmin(admin.ModelAdmin):
    list_display = ['candidatura', 'tipo', 'data_hora', 'status_badge', 'parecer_badge']
    list_filter = ['tipo', 'status', 'parecer']
    filter_horizontal = ['entrevistadores']
    
    def status_badge(self, obj):
        colors = {
            'agendada': '#3498db',
            'confirmada': '#27ae60',
            'realizada': '#2ecc71',
            'cancelada': '#e74c3c',
            'remarcada': '#f39c12',
            'no_show': '#95a5a6',
        }
        return format_html(
            '<span style="background:{};color:white;padding:3px 10px;border-radius:3px;">{}</span>',
            colors.get(obj.status, '#95a5a6'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def parecer_badge(self, obj):
        colors = {'aprovado': '#27ae60', 'reprovado': '#e74c3c', 'pendente': '#f39c12'}
        if obj.parecer:
            return format_html(
                '<span style="background:{};color:white;padding:3px 10px;border-radius:3px;">{}</span>',
                colors.get(obj.parecer, '#95a5a6'),
                obj.get_parecer_display()
            )
        return '-'
    parecer_badge.short_description = 'Parecer'


# =====================================================
# MÉTRICAS
# =====================================================

@admin.register(MetricaRecrutamento)
class MetricaRecrutamentoAdmin(admin.ModelAdmin):
    list_display = ['periodo_inicio', 'periodo_fim', 'total_candidatos', 'candidatos_contratados', 'taxa_conversao_final', 'tempo_medio_preenchimento']
    list_filter = ['vaga']
    date_hierarchy = 'periodo_fim'


# =====================================================
# PÁGINA DE CARREIRAS
# =====================================================

class DepoimentoColaboradorInline(admin.TabularInline):
    model = DepoimentoColaborador
    extra = 1


@admin.register(PaginaCarreiras)
class PaginaCarreirasAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'cor_preview']
    inlines = [DepoimentoColaboradorInline]
    
    def cor_preview(self, obj):
        return format_html(
            '<span style="background:{};padding:5px 15px;border-radius:3px;"></span> '
            '<span style="background:{};padding:5px 15px;border-radius:3px;"></span>',
            obj.cor_primaria, obj.cor_secundaria
        )
    cor_preview.short_description = 'Cores'


# =====================================================
# IA
# =====================================================

@admin.register(SugestaoIA)
class SugestaoIAAdmin(admin.ModelAdmin):
    list_display = ['tipo', 'vaga', 'candidato', 'utilizado', 'avaliacao', 'solicitado_por', 'created_at']
    list_filter = ['tipo', 'utilizado']
    search_fields = ['conteudo']
    readonly_fields = ['prompt_usado', 'conteudo', 'contexto']
