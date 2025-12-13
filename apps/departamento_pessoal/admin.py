"""
Admin do Módulo Departamento Pessoal - SyncRH
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import (
    Colaborador, Departamento, Cargo, EscalaTrabalho,
    RegistroPonto, JustificativaPonto,
    FolhaPagamento,
    ProcessoAdmissao, DocumentoAdmissao,
    CategoriaDocumento, DocumentoGED,
    PeriodoAquisitivo, SolicitacaoFerias, FeriasColetivas,
    Contador, ExportacaoContabil
)


# =====================================================
# CONTROLE DE PONTO
# =====================================================

@admin.register(Colaborador)
class ColaboradorAdmin(admin.ModelAdmin):
    list_display = ['nome_completo', 'cpf', 'cargo', 'departamento', 'data_admissao', 'status_badge']
    list_filter = ['is_active', 'departamento', 'cargo', 'data_admissao']
    search_fields = ['nome_completo', 'cpf', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['user', 'cargo', 'departamento', 'gestor']
    
    fieldsets = (
        ('Dados Pessoais', {
            'fields': ('user', 'nome_completo', 'cpf', 'data_nascimento', 'foto_perfil')
        }),
        ('Dados Profissionais', {
            'fields': ('cargo', 'departamento', 'gestor', 'data_admissao', 'data_demissao')
        }),
        ('Contato', {
            'fields': ('email_pessoal', 'telefone', 'endereco')
        }),
        ('Dados Bancários', {
            'fields': ('banco', 'agencia', 'conta', 'tipo_conta'),
            'classes': ('collapse',)
        }),
        ('Reconhecimento Facial', {
            'fields': ('face_encoding',),
            'classes': ('collapse',)
        }),
        ('Auditoria', {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        if obj.data_demissao:
            return format_html('<span style="background:#e74c3c;color:white;padding:3px 10px;border-radius:3px;">Desligado</span>')
        elif obj.is_active:
            return format_html('<span style="background:#27ae60;color:white;padding:3px 10px;border-radius:3px;">Ativo</span>')
        return format_html('<span style="background:#95a5a6;color:white;padding:3px 10px;border-radius:3px;">Inativo</span>')
    status_badge.short_description = 'Status'


@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'codigo', 'responsavel', 'total_colaboradores']
    search_fields = ['nome', 'codigo']
    
    def total_colaboradores(self, obj):
        return obj.colaboradores.count()
    total_colaboradores.short_description = 'Colaboradores'


@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'codigo', 'nivel', 'departamento', 'salario_base']
    list_filter = ['nivel', 'departamento']
    search_fields = ['nome', 'codigo', 'cbo']


@admin.register(EscalaTrabalho)
class EscalaTrabalhoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'tipo', 'hora_entrada', 'hora_saida', 'horas_semanais']
    list_filter = ['tipo']


@admin.register(RegistroPonto)
class RegistroPontoAdmin(admin.ModelAdmin):
    list_display = ['colaborador', 'data', 'entrada', 'saida', 'horas_trabalhadas', 'status_badge', 'tipo_registro']
    list_filter = ['status', 'tipo_registro', 'data', 'validado_facial']
    search_fields = ['colaborador__nome_completo']
    date_hierarchy = 'data'
    readonly_fields = ['horas_trabalhadas', 'horas_extras', 'horas_faltantes']
    
    def status_badge(self, obj):
        colors = {
            'pendente': '#f39c12',
            'aprovado': '#27ae60',
            'rejeitado': '#e74c3c',
            'ajustado': '#3498db',
        }
        return format_html(
            '<span style="background:{};color:white;padding:3px 10px;border-radius:3px;">{}</span>',
            colors.get(obj.status, '#95a5a6'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(JustificativaPonto)
class JustificativaPontoAdmin(admin.ModelAdmin):
    list_display = ['registro', 'tipo', 'aprovado_por', 'data_aprovacao']
    list_filter = ['tipo']


# =====================================================
# FOLHA DE PAGAMENTO
# =====================================================

@admin.register(FolhaPagamento)
class FolhaPagamentoAdmin(admin.ModelAdmin):
    list_display = ['colaborador', 'competencia', 'salario_base', 'total_proventos', 'total_descontos', 'salario_liquido', 'status_badge']
    list_filter = ['status', 'competencia', 'esocial_enviado']
    search_fields = ['colaborador__nome_completo']
    date_hierarchy = 'competencia'
    readonly_fields = ['total_proventos', 'total_descontos', 'salario_liquido']
    
    fieldsets = (
        ('Identificação', {
            'fields': ('colaborador', 'competencia', 'status')
        }),
        ('Proventos', {
            'fields': ('salario_base', 'horas_extras', 'adicional_noturno', 'comissoes', 'bonus', 'outros_proventos')
        }),
        ('Descontos', {
            'fields': ('inss', 'irrf', 'vale_transporte', 'vale_alimentacao', 'plano_saude', 'emprestimos', 'faltas', 'outros_descontos')
        }),
        ('Totais', {
            'fields': ('total_proventos', 'total_descontos', 'salario_liquido', 'data_pagamento')
        }),
        ('eSocial', {
            'fields': ('esocial_enviado', 'esocial_protocolo', 'esocial_data_envio'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        colors = {
            'rascunho': '#95a5a6',
            'calculada': '#f39c12',
            'aprovada': '#3498db',
            'paga': '#27ae60',
            'cancelada': '#e74c3c',
        }
        return format_html(
            '<span style="background:{};color:white;padding:3px 10px;border-radius:3px;">{}</span>',
            colors.get(obj.status, '#95a5a6'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'


# =====================================================
# ADMISSÃO
# =====================================================

class DocumentoAdmissaoInline(admin.TabularInline):
    model = DocumentoAdmissao
    extra = 0
    readonly_fields = ['validado', 'validado_por', 'data_validacao']


@admin.register(ProcessoAdmissao)
class ProcessoAdmissaoAdmin(admin.ModelAdmin):
    list_display = ['candidato_nome', 'candidato_email', 'cargo_pretendido', 'data_prevista_admissao', 'status_badge', 'documentos_count']
    list_filter = ['status', 'cargo_pretendido', 'departamento']
    search_fields = ['candidato_nome', 'candidato_email', 'candidato_cpf']
    inlines = [DocumentoAdmissaoInline]
    readonly_fields = ['token_acesso', 'colaborador_criado']
    
    def status_badge(self, obj):
        colors = {
            'aguardando_documentos': '#f39c12',
            'documentos_enviados': '#3498db',
            'em_analise': '#9b59b6',
            'pendente_assinatura': '#e67e22',
            'assinado': '#27ae60',
            'concluido': '#2ecc71',
            'cancelado': '#e74c3c',
        }
        return format_html(
            '<span style="background:{};color:white;padding:3px 10px;border-radius:3px;">{}</span>',
            colors.get(obj.status, '#95a5a6'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def documentos_count(self, obj):
        total = obj.documentos.count()
        validados = obj.documentos.filter(validado=True).count()
        return f"{validados}/{total}"
    documentos_count.short_description = 'Documentos'


# =====================================================
# GED
# =====================================================

@admin.register(CategoriaDocumento)
class CategoriaDocumentoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cor_preview', 'total_documentos']
    
    def cor_preview(self, obj):
        return format_html(
            '<span style="background:{};color:white;padding:3px 15px;border-radius:3px;">{}</span>',
            obj.cor, obj.cor
        )
    cor_preview.short_description = 'Cor'
    
    def total_documentos(self, obj):
        return obj.documentos.count()
    total_documentos.short_description = 'Documentos'


@admin.register(DocumentoGED)
class DocumentoGEDAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'categoria', 'colaborador', 'versao', 'vencimento_badge', 'assinado_badge']
    list_filter = ['categoria', 'assinado_digitalmente', 'publico']
    search_fields = ['titulo', 'colaborador__nome_completo']
    filter_horizontal = ['compartilhado_com']
    
    def vencimento_badge(self, obj):
        if not obj.data_vencimento:
            return '-'
        dias = (obj.data_vencimento - timezone.now().date()).days
        if dias < 0:
            return format_html('<span style="background:#e74c3c;color:white;padding:3px 10px;border-radius:3px;">Vencido</span>')
        elif dias <= obj.alerta_vencimento_dias:
            return format_html('<span style="background:#f39c12;color:white;padding:3px 10px;border-radius:3px;">{}d</span>', dias)
        return format_html('<span style="background:#27ae60;color:white;padding:3px 10px;border-radius:3px;">{}d</span>', dias)
    vencimento_badge.short_description = 'Vencimento'
    
    def assinado_badge(self, obj):
        if obj.assinado_digitalmente:
            return format_html('<span style="color:#27ae60;">✓ Assinado</span>')
        return format_html('<span style="color:#95a5a6;">-</span>')
    assinado_badge.short_description = 'Assinatura'


# =====================================================
# FÉRIAS
# =====================================================

@admin.register(PeriodoAquisitivo)
class PeriodoAquisitivoAdmin(admin.ModelAdmin):
    list_display = ['colaborador', 'data_inicio', 'data_fim', 'dias_direito', 'dias_gozados', 'dias_restantes', 'vencido_badge']
    list_filter = ['vencido']
    search_fields = ['colaborador__nome_completo']
    
    def vencido_badge(self, obj):
        if obj.vencido:
            return format_html('<span style="background:#e74c3c;color:white;padding:3px 10px;border-radius:3px;">Vencido</span>')
        return format_html('<span style="background:#27ae60;color:white;padding:3px 10px;border-radius:3px;">OK</span>')
    vencido_badge.short_description = 'Status'


@admin.register(SolicitacaoFerias)
class SolicitacaoFeriasAdmin(admin.ModelAdmin):
    list_display = ['colaborador', 'data_inicio', 'data_fim', 'dias_solicitados', 'vender_dias', 'status_badge']
    list_filter = ['status', 'adiantar_13']
    search_fields = ['colaborador__nome_completo']
    
    def status_badge(self, obj):
        colors = {
            'rascunho': '#95a5a6',
            'pendente': '#f39c12',
            'aprovado_gestor': '#3498db',
            'aprovado_dp': '#27ae60',
            'rejeitado': '#e74c3c',
            'cancelado': '#7f8c8d',
            'em_gozo': '#9b59b6',
            'concluido': '#2ecc71',
        }
        return format_html(
            '<span style="background:{};color:white;padding:3px 10px;border-radius:3px;">{}</span>',
            colors.get(obj.status, '#95a5a6'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(FeriasColetivas)
class FeriasColetivasAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'data_inicio', 'data_fim', 'dias', 'status']
    list_filter = ['status']
    filter_horizontal = ['departamentos', 'colaboradores_excluidos']


# =====================================================
# INTEGRAÇÃO CONTÁBIL
# =====================================================

@admin.register(Contador)
class ContadorAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cnpj', 'crc', 'email']
    search_fields = ['nome', 'cnpj', 'crc']


@admin.register(ExportacaoContabil)
class ExportacaoContabilAdmin(admin.ModelAdmin):
    list_display = ['contador', 'competencia', 'tipo', 'formato', 'status_badge', 'baixado_em']
    list_filter = ['status', 'tipo', 'formato']
    
    def status_badge(self, obj):
        colors = {
            'gerando': '#f39c12',
            'disponivel': '#27ae60',
            'baixado': '#3498db',
            'erro': '#e74c3c',
        }
        return format_html(
            '<span style="background:{};color:white;padding:3px 10px;border-radius:3px;">{}</span>',
            colors.get(obj.status, '#95a5a6'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
