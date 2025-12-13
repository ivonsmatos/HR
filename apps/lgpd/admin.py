"""
SyncRH - Admin LGPD
===================
Administração dos modelos de conformidade LGPD
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone

from .models import (
    RegistroTratamento,
    TermoConsentimento,
    ConsentimentoTitular,
    SolicitacaoTitular,
    RegistroAnonimizacao,
    RelatorioImpacto,
    IncidenteSeguranca,
    LogAcessoDados
)


@admin.register(RegistroTratamento)
class RegistroTratamentoAdmin(admin.ModelAdmin):
    list_display = [
        'nome', 'finalidade', 'base_legal', 'categoria_dados',
        'departamento_responsavel', 'ativo', 'created_at'
    ]
    list_filter = ['base_legal', 'categoria_dados', 'ativo', 'transferencia_internacional']
    search_fields = ['nome', 'finalidade', 'descricao']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Identificação', {
            'fields': ('nome', 'finalidade', 'descricao')
        }),
        ('Base Legal', {
            'fields': ('base_legal', 'categoria_dados', 'categoria_titulares')
        }),
        ('Responsabilidades', {
            'fields': ('departamento_responsavel', 'responsavel_tratamento')
        }),
        ('Transferência', {
            'fields': ('transferencia_internacional', 'pais_destino', 'garantias_transferencia')
        }),
        ('Retenção', {
            'fields': ('prazo_retencao', 'justificativa_retencao')
        }),
        ('Status', {
            'fields': ('ativo', 'created_at', 'updated_at')
        }),
    )


@admin.register(TermoConsentimento)
class TermoConsentimentoAdmin(admin.ModelAdmin):
    list_display = [
        'titulo', 'versao', 'data_vigencia_inicio', 
        'data_vigencia_fim', 'obrigatorio', 'ativo'
    ]
    list_filter = ['obrigatorio', 'ativo', 'finalidades']
    search_fields = ['titulo', 'texto_completo']
    readonly_fields = ['versao', 'created_at', 'hash_conteudo']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('titulo', 'texto_completo', 'versao', 'hash_conteudo')
        }),
        ('Finalidades', {
            'fields': ('finalidades',)
        }),
        ('Vigência', {
            'fields': ('data_vigencia_inicio', 'data_vigencia_fim')
        }),
        ('Configurações', {
            'fields': ('obrigatorio', 'ativo')
        }),
    )


@admin.register(ConsentimentoTitular)
class ConsentimentoTitularAdmin(admin.ModelAdmin):
    list_display = [
        'titular', 'termo', 'data_consentimento', 
        'status_consentimento', 'data_revogacao'
    ]
    list_filter = ['termo', 'data_consentimento', 'data_revogacao']
    search_fields = ['titular__username', 'titular__email']
    readonly_fields = [
        'data_consentimento', 'data_revogacao', 'hash_consentimento',
        'ip_address', 'user_agent'
    ]
    raw_id_fields = ['titular', 'termo']
    
    def status_consentimento(self, obj):
        if obj.esta_ativo:
            return format_html('<span style="color: green;">✓ Ativo</span>')
        return format_html('<span style="color: red;">✗ Revogado</span>')
    status_consentimento.short_description = 'Status'


@admin.register(SolicitacaoTitular)
class SolicitacaoTitularAdmin(admin.ModelAdmin):
    list_display = [
        'protocolo', 'titular', 'tipo', 'status', 
        'created_at', 'data_limite', 'prazo_status'
    ]
    list_filter = ['tipo', 'status', 'created_at']
    search_fields = ['protocolo', 'titular__username', 'titular__email']
    readonly_fields = ['protocolo', 'created_at', 'data_limite']
    raw_id_fields = ['titular', 'responsavel']
    
    fieldsets = (
        ('Identificação', {
            'fields': ('protocolo', 'titular', 'tipo')
        }),
        ('Detalhes', {
            'fields': ('descricao', 'email_contato')
        }),
        ('Processamento', {
            'fields': ('status', 'responsavel', 'resposta', 'data_resposta')
        }),
        ('Prazos', {
            'fields': ('created_at', 'data_limite')
        }),
        ('Anexos', {
            'fields': ('documentos_anexos',)
        }),
    )
    
    def prazo_status(self, obj):
        if obj.status == 'concluida':
            return format_html('<span style="color: green;">Concluída</span>')
        
        dias_restantes = (obj.data_limite - timezone.now().date()).days
        
        if dias_restantes < 0:
            return format_html(
                '<span style="color: red; font-weight: bold;">⚠ Atrasada ({} dias)</span>',
                abs(dias_restantes)
            )
        elif dias_restantes <= 3:
            return format_html(
                '<span style="color: orange;">⚠ {} dias restantes</span>',
                dias_restantes
            )
        return format_html(
            '<span style="color: green;">{} dias restantes</span>',
            dias_restantes
        )
    prazo_status.short_description = 'Prazo'


@admin.register(RegistroAnonimizacao)
class RegistroAnonimizacaoAdmin(admin.ModelAdmin):
    list_display = [
        'modelo', 'tipo', 'quantidade_registros', 
        'reversivel', 'executado_por', 'created_at'
    ]
    list_filter = ['tipo', 'modelo', 'reversivel', 'created_at']
    search_fields = ['modelo', 'motivo', 'descricao']
    readonly_fields = ['created_at']


@admin.register(RelatorioImpacto)
class RelatorioImpactoAdmin(admin.ModelAdmin):
    list_display = [
        'titulo', 'registro_tratamento', 'nivel_risco_inicial',
        'nivel_risco_residual', 'status', 'data_elaboracao'
    ]
    list_filter = ['status', 'nivel_risco_inicial', 'nivel_risco_residual']
    search_fields = ['titulo', 'descricao_tratamento']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['registro_tratamento', 'elaborado_por', 'aprovado_por']
    
    fieldsets = (
        ('Identificação', {
            'fields': ('titulo', 'registro_tratamento', 'elaborado_por')
        }),
        ('Descrição do Tratamento', {
            'fields': ('descricao_tratamento', 'necessidade_proporcionalidade')
        }),
        ('Análise de Riscos', {
            'fields': (
                'riscos_identificados', 'nivel_risco_inicial',
                'medidas_mitigacao', 'nivel_risco_residual'
            )
        }),
        ('Consulta ao Titular', {
            'fields': ('consulta_titular', 'parecer_dpo')
        }),
        ('Aprovação', {
            'fields': ('status', 'aprovado_por', 'data_aprovacao', 'observacoes_aprovacao')
        }),
        ('Datas', {
            'fields': ('data_elaboracao', 'data_revisao', 'created_at', 'updated_at')
        }),
    )


@admin.register(IncidenteSeguranca)
class IncidenteSegurancaAdmin(admin.ModelAdmin):
    list_display = [
        'protocolo', 'tipo_incidente', 'severidade', 'status',
        'comunicado_anpd', 'comunicado_titulares', 'created_at'
    ]
    list_filter = ['tipo_incidente', 'severidade', 'status', 'comunicado_anpd']
    search_fields = ['protocolo', 'descricao', 'sistemas_afetados']
    readonly_fields = ['protocolo', 'created_at', 'updated_at']
    raw_id_fields = ['reportado_por', 'responsavel_resposta']
    
    fieldsets = (
        ('Identificação', {
            'fields': ('protocolo', 'tipo_incidente', 'severidade', 'status')
        }),
        ('Descrição', {
            'fields': ('descricao', 'sistemas_afetados', 'dados_comprometidos')
        }),
        ('Impacto', {
            'fields': ('quantidade_titulares_afetados', 'categorias_dados_afetados')
        }),
        ('Cronologia', {
            'fields': ('data_deteccao', 'data_inicio_incidente', 'data_contencao')
        }),
        ('Resposta', {
            'fields': ('reportado_por', 'responsavel_resposta', 'acoes_tomadas')
        }),
        ('Comunicações', {
            'fields': (
                'comunicado_anpd', 'data_comunicacao_anpd', 'protocolo_anpd',
                'comunicado_titulares', 'data_comunicacao_titulares'
            )
        }),
        ('Pós-Incidente', {
            'fields': ('licoes_aprendidas', 'acoes_preventivas')
        }),
    )


@admin.register(LogAcessoDados)
class LogAcessoDadosAdmin(admin.ModelAdmin):
    list_display = [
        'usuario', 'modelo_acessado', 'tipo_operacao', 
        'finalidade', 'created_at'
    ]
    list_filter = ['tipo_operacao', 'finalidade', 'modelo_acessado', 'created_at']
    search_fields = ['usuario__username', 'modelo_acessado', 'justificativa']
    readonly_fields = ['created_at', 'hash_registro']
    
    def has_change_permission(self, request, obj=None):
        return False  # Logs não podem ser alterados
    
    def has_delete_permission(self, request, obj=None):
        return False  # Logs não podem ser deletados
