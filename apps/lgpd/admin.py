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
        'nome', 'finalidade', 'base_legal', 'transferencia_internacional',
        'controlador', 'is_active', 'created_at'
    ]
    list_filter = ['base_legal', 'finalidade', 'is_active', 'transferencia_internacional']
    search_fields = ['nome', 'descricao', 'controlador', 'encarregado_dpo']
    readonly_fields = ['created_at', 'updated_at', 'uuid']
    raw_id_fields = ['aprovado_por']
    
    fieldsets = (
        ('Identificação', {
            'fields': ('nome', 'descricao', 'uuid')
        }),
        ('Base Legal e Finalidade', {
            'fields': ('base_legal', 'finalidade')
        }),
        ('Dados Tratados', {
            'fields': ('dados_pessoais', 'dados_sensiveis', 'categorias_titulares')
        }),
        ('Compartilhamento', {
            'fields': ('destinatarios', 'transferencia_internacional', 'paises_transferencia')
        }),
        ('Retenção', {
            'fields': ('prazo_retencao_dias', 'justificativa_retencao')
        }),
        ('Segurança', {
            'fields': ('medidas_seguranca',)
        }),
        ('Responsáveis', {
            'fields': ('controlador', 'operador', 'encarregado_dpo')
        }),
        ('Aprovação', {
            'fields': ('aprovado_por', 'data_aprovacao')
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )


@admin.register(TermoConsentimento)
class TermoConsentimentoAdmin(admin.ModelAdmin):
    list_display = [
        'titulo', 'versao', 'data_vigencia_inicio', 
        'data_vigencia_fim', 'is_active'
    ]
    list_filter = ['is_active', 'data_vigencia_inicio']
    search_fields = ['titulo', 'conteudo']
    readonly_fields = ['created_at', 'updated_at', 'uuid']
    raw_id_fields = ['aprovado_por']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('titulo', 'versao', 'conteudo', 'uuid')
        }),
        ('Finalidades', {
            'fields': ('finalidades',)
        }),
        ('Vigência', {
            'fields': ('data_vigencia_inicio', 'data_vigencia_fim')
        }),
        ('Aprovação', {
            'fields': ('aprovado_por',)
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
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
        'ip_address', 'user_agent', 'created_at', 'updated_at', 'uuid'
    ]
    raw_id_fields = ['titular', 'termo']
    
    fieldsets = (
        ('Titular e Termo', {
            'fields': ('titular', 'termo', 'uuid')
        }),
        ('Consentimento', {
            'fields': ('finalidades_aceitas', 'data_consentimento', 'hash_consentimento')
        }),
        ('Revogação', {
            'fields': ('data_revogacao', 'motivo_revogacao')
        }),
        ('Informações Técnicas', {
            'fields': ('ip_address', 'user_agent')
        }),
        ('Metadados', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )
    
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
    readonly_fields = ['protocolo', 'created_at', 'updated_at', 'uuid']
    raw_id_fields = ['titular', 'responsavel']
    
    fieldsets = (
        ('Identificação', {
            'fields': ('protocolo', 'titular', 'tipo', 'uuid')
        }),
        ('Detalhes', {
            'fields': ('descricao', 'dados_solicitados', 'email_contato')
        }),
        ('Processamento', {
            'fields': ('status', 'responsavel', 'resposta', 'data_resposta')
        }),
        ('Negativa', {
            'fields': ('justificativa_negativa',)
        }),
        ('Prazos', {
            'fields': ('created_at', 'data_limite')
        }),
        ('Anexos', {
            'fields': ('arquivo_resposta',)
        }),
        ('Metadados', {
            'fields': ('is_active', 'updated_at')
        }),
    )
    
    def prazo_status(self, obj):
        if obj.status == 'concluida':
            return format_html('<span style="color: green;">Concluída</span>')
        
        if obj.data_limite:
            dias_restantes = (obj.data_limite.date() - timezone.now().date()).days
            
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
        return '-'
    prazo_status.short_description = 'Prazo'


@admin.register(RegistroAnonimizacao)
class RegistroAnonimizacaoAdmin(admin.ModelAdmin):
    list_display = [
        'modelo', 'tipo', 'quantidade_registros', 
        'reversivel', 'executado_por', 'created_at'
    ]
    list_filter = ['tipo', 'modelo', 'reversivel', 'created_at']
    search_fields = ['modelo', 'motivo', 'descricao']
    readonly_fields = ['created_at', 'updated_at', 'uuid', 'data_execucao']
    raw_id_fields = ['executado_por']
    
    fieldsets = (
        ('Identificação', {
            'fields': ('tipo', 'motivo', 'descricao', 'uuid')
        }),
        ('Dados Afetados', {
            'fields': ('modelo', 'campos', 'quantidade_registros')
        }),
        ('Técnica', {
            'fields': ('tecnica', 'reversivel')
        }),
        ('Execução', {
            'fields': ('executado_por', 'data_execucao')
        }),
        ('Metadados', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )


@admin.register(RelatorioImpacto)
class RelatorioImpactoAdmin(admin.ModelAdmin):
    list_display = [
        'titulo', 'versao', 'registro_tratamento', 'probabilidade_risco',
        'impacto_risco', 'status', 'created_at'
    ]
    list_filter = ['status', 'probabilidade_risco', 'impacto_risco']
    search_fields = ['titulo', 'descricao_tratamento']
    readonly_fields = ['created_at', 'updated_at', 'uuid']
    raw_id_fields = ['registro_tratamento', 'elaborado_por', 'aprovado_por']
    
    fieldsets = (
        ('Identificação', {
            'fields': ('titulo', 'versao', 'registro_tratamento', 'uuid')
        }),
        ('Elaboração', {
            'fields': ('elaborado_por',)
        }),
        ('Descrição do Tratamento', {
            'fields': ('descricao_tratamento', 'necessidade_proporcionalidade')
        }),
        ('Análise de Riscos', {
            'fields': (
                'riscos_identificados', 'probabilidade_risco', 'impacto_risco'
            )
        }),
        ('Medidas Mitigadoras', {
            'fields': ('medidas_mitigadoras', 'riscos_residuais')
        }),
        ('Parecer do DPO', {
            'fields': ('parecer_dpo', 'data_parecer_dpo')
        }),
        ('Aprovação', {
            'fields': ('status', 'aprovado_por', 'data_aprovacao')
        }),
        ('Metadados', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )


@admin.register(IncidenteSeguranca)
class IncidenteSegurancaAdmin(admin.ModelAdmin):
    list_display = [
        'protocolo', 'titulo', 'tipo_incidente', 'severidade', 'status',
        'comunicado_anpd', 'comunicado_titulares', 'created_at'
    ]
    list_filter = ['tipo_incidente', 'severidade', 'status', 'comunicado_anpd']
    search_fields = ['protocolo', 'titulo', 'descricao']
    readonly_fields = ['protocolo', 'created_at', 'updated_at', 'uuid']
    raw_id_fields = ['reportado_por', 'responsavel_investigacao']
    
    fieldsets = (
        ('Identificação', {
            'fields': ('protocolo', 'titulo', 'uuid')
        }),
        ('Classificação', {
            'fields': ('tipo_incidente', 'severidade', 'status')
        }),
        ('Descrição', {
            'fields': ('descricao',)
        }),
        ('Dados Afetados', {
            'fields': ('dados_afetados', 'quantidade_titulares', 'categorias_titulares')
        }),
        ('Cronologia', {
            'fields': ('data_ocorrencia', 'data_deteccao', 'data_contencao', 'data_resolucao')
        }),
        ('Responsáveis', {
            'fields': ('reportado_por', 'responsavel_investigacao')
        }),
        ('Investigação', {
            'fields': ('causa_raiz', 'acoes_tomadas', 'medidas_preventivas')
        }),
        ('Comunicação ANPD', {
            'fields': ('comunicado_anpd', 'data_comunicacao_anpd', 'protocolo_anpd')
        }),
        ('Comunicação aos Titulares', {
            'fields': ('comunicado_titulares', 'data_comunicacao_titulares', 'metodo_comunicacao_titulares')
        }),
        ('Metadados', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )


@admin.register(LogAcessoDados)
class LogAcessoDadosAdmin(admin.ModelAdmin):
    list_display = [
        'usuario', 'modelo', 'operacao', 
        'finalidade', 'data_acesso'
    ]
    list_filter = ['operacao', 'modelo', 'data_acesso']
    search_fields = ['usuario__username', 'modelo', 'finalidade', 'endpoint']
    readonly_fields = [
        'created_at', 'updated_at', 'uuid', 'data_acesso',
        'usuario', 'modelo', 'objeto_id', 'campos_acessados',
        'operacao', 'finalidade', 'ip_address', 'user_agent', 'endpoint'
    ]
    
    fieldsets = (
        ('Usuário', {
            'fields': ('usuario', 'uuid')
        }),
        ('Dados Acessados', {
            'fields': ('modelo', 'objeto_id', 'campos_acessados')
        }),
        ('Operação', {
            'fields': ('operacao', 'finalidade')
        }),
        ('Contexto', {
            'fields': ('ip_address', 'user_agent', 'endpoint')
        }),
        ('Timestamps', {
            'fields': ('data_acesso', 'created_at', 'updated_at')
        }),
    )
    
    def has_add_permission(self, request):
        return False  # Logs não podem ser criados manualmente
    
    def has_change_permission(self, request, obj=None):
        return False  # Logs não podem ser alterados
    
    def has_delete_permission(self, request, obj=None):
        return False  # Logs não podem ser deletados
