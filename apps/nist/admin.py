"""
SyncRH - Admin NIST
===================
Administração dos modelos NIST Cybersecurity Framework
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone

from .models import (
    AtivoInformacao,
    AvaliacaoRisco,
    ControleAcesso,
    ConfiguracaoSeguranca,
    TreinamentoSeguranca,
    RegraDeteccao,
    AlertaSeguranca,
    PlanoRespostaIncidente,
    AcaoResposta,
    PlanoRecuperacao,
    TesteRecuperacao,
    BackupRegistro
)


# ============================================
# IDENTIFY (ID) - Identificar
# ============================================

@admin.register(AtivoInformacao)
class AtivoInformacaoAdmin(admin.ModelAdmin):
    list_display = [
        'nome', 'tipo', 'classificacao', 'valor_negocio',
        'proprietario', 'ambiente', 'created_at'
    ]
    list_filter = ['tipo', 'classificacao', 'valor_negocio', 'ambiente']
    search_fields = ['nome', 'descricao', 'localizacao']
    readonly_fields = ['created_at', 'updated_at', 'uuid']
    raw_id_fields = ['proprietario', 'custodiante']
    
    fieldsets = (
        ('Identificação', {
            'fields': ('uuid', 'nome', 'descricao', 'tipo')
        }),
        ('Classificação', {
            'fields': ('classificacao', 'valor_negocio')
        }),
        ('Responsabilidade', {
            'fields': ('proprietario', 'custodiante')
        }),
        ('Localização', {
            'fields': ('localizacao', 'ambiente')
        }),
        ('Metadados', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )


@admin.register(AvaliacaoRisco)
class AvaliacaoRiscoAdmin(admin.ModelAdmin):
    list_display = [
        'titulo', 'ativo', 'ameaca', 'probabilidade', 'impacto',
        'nivel_risco_display', 'status', 'responsavel'
    ]
    list_filter = ['status', 'probabilidade', 'impacto', 'created_at']
    search_fields = ['titulo', 'ameaca', 'vulnerabilidade', 'descricao']
    readonly_fields = ['created_at', 'updated_at', 'uuid']
    raw_id_fields = ['ativo', 'responsavel']
    
    fieldsets = (
        ('Identificação', {
            'fields': ('uuid', 'titulo', 'descricao', 'ativo')
        }),
        ('Análise de Risco', {
            'fields': ('ameaca', 'vulnerabilidade', 'probabilidade', 'impacto')
        }),
        ('Tratamento', {
            'fields': ('status', 'estrategia_tratamento', 'plano_acao', 'risco_residual')
        }),
        ('Responsabilidade', {
            'fields': ('responsavel', 'data_revisao')
        }),
        ('Metadados', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )
    
    def nivel_risco_display(self, obj):
        nivel = obj.nivel_risco
        if nivel >= 20:
            color = 'red'
        elif nivel >= 13:
            color = 'orange'
        elif nivel >= 9:
            color = 'gold'
        else:
            color = 'green'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}/25</span>',
            color, nivel
        )
    nivel_risco_display.short_description = 'Nível de Risco'


# ============================================
# PROTECT (PR) - Proteger
# ============================================

@admin.register(ControleAcesso)
class ControleAcessoAdmin(admin.ModelAdmin):
    list_display = [
        'ativo', 'tipo', 'status', 'efetividade',
        'ultima_verificacao', 'is_active'
    ]
    list_filter = ['tipo', 'status', 'efetividade', 'is_active']
    search_fields = ['descricao', 'implementacao']
    readonly_fields = ['created_at', 'updated_at', 'uuid']
    raw_id_fields = ['ativo']
    
    fieldsets = (
        ('Identificação', {
            'fields': ('uuid', 'ativo', 'tipo', 'descricao')
        }),
        ('Configuração', {
            'fields': ('requisitos', 'implementacao')
        }),
        ('Status', {
            'fields': ('status', 'efetividade', 'ultima_verificacao')
        }),
        ('Metadados', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )


@admin.register(ConfiguracaoSeguranca)
class ConfiguracaoSegurancaAdmin(admin.ModelAdmin):
    list_display = [
        'nome', 'tipo_sistema', 'versao', 'data_aprovacao',
        'proxima_revisao', 'is_active'
    ]
    list_filter = ['tipo_sistema', 'is_active']
    search_fields = ['nome', 'versao']
    readonly_fields = ['created_at', 'updated_at', 'uuid']
    
    fieldsets = (
        ('Identificação', {
            'fields': ('uuid', 'nome', 'tipo_sistema', 'versao')
        }),
        ('Configurações', {
            'fields': ('configuracoes', 'frameworks')
        }),
        ('Validade', {
            'fields': ('data_aprovacao', 'proxima_revisao')
        }),
        ('Metadados', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )


@admin.register(TreinamentoSeguranca)
class TreinamentoSegurancaAdmin(admin.ModelAdmin):
    list_display = [
        'titulo', 'tipo', 'carga_horaria', 'obrigatorio',
        'validade_dias', 'is_active'
    ]
    list_filter = ['tipo', 'obrigatorio', 'is_active']
    search_fields = ['titulo', 'descricao']
    readonly_fields = ['created_at', 'updated_at', 'uuid']
    
    fieldsets = (
        ('Identificação', {
            'fields': ('uuid', 'titulo', 'descricao', 'tipo')
        }),
        ('Configuração', {
            'fields': ('obrigatorio', 'publico_alvo', 'carga_horaria', 'validade_dias')
        }),
        ('Metadados', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )


# ============================================
# DETECT (DE) - Detectar
# ============================================

@admin.register(RegraDeteccao)
class RegraDeteccaoAdmin(admin.ModelAdmin):
    list_display = [
        'nome', 'tipo', 'severidade', 'habilitada', 'is_active'
    ]
    list_filter = ['tipo', 'severidade', 'habilitada', 'is_active']
    search_fields = ['nome', 'descricao']
    readonly_fields = ['created_at', 'updated_at', 'uuid']
    
    fieldsets = (
        ('Identificação', {
            'fields': ('uuid', 'nome', 'descricao', 'tipo')
        }),
        ('Configuração', {
            'fields': ('condicoes', 'severidade', 'acoes')
        }),
        ('Status', {
            'fields': ('habilitada',)
        }),
        ('Metadados', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )


@admin.register(AlertaSeguranca)
class AlertaSegurancaAdmin(admin.ModelAdmin):
    list_display = [
        'titulo', 'regra', 'severidade_display', 'status',
        'atribuido_para', 'created_at'
    ]
    list_filter = ['severidade', 'status', 'created_at']
    search_fields = ['titulo', 'descricao', 'fonte']
    readonly_fields = ['created_at', 'updated_at', 'uuid']
    raw_id_fields = ['regra', 'atribuido_para']
    
    fieldsets = (
        ('Identificação', {
            'fields': ('uuid', 'titulo', 'descricao', 'regra')
        }),
        ('Detalhes', {
            'fields': ('severidade', 'fonte', 'dados_evento')
        }),
        ('Afetados', {
            'fields': ('usuarios_afetados', 'ativos_afetados')
        }),
        ('Tratamento', {
            'fields': ('status', 'atribuido_para', 'analise', 'data_resolucao')
        }),
        ('Metadados', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )
    
    def severidade_display(self, obj):
        cores = {
            'baixa': 'green',
            'media': 'gold',
            'alta': 'orange',
            'critica': 'red'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            cores.get(obj.severidade, 'gray'),
            obj.get_severidade_display()
        )
    severidade_display.short_description = 'Severidade'


# ============================================
# RESPOND (RS) - Responder
# ============================================

@admin.register(PlanoRespostaIncidente)
class PlanoRespostaIncidenteAdmin(admin.ModelAdmin):
    list_display = [
        'nome', 'versao', 'tipo_incidente', 'aprovado_por',
        'data_aprovacao', 'proxima_revisao'
    ]
    list_filter = ['tipo_incidente', 'is_active']
    search_fields = ['nome']
    readonly_fields = ['created_at', 'updated_at', 'uuid']
    raw_id_fields = ['aprovado_por']
    
    fieldsets = (
        ('Identificação', {
            'fields': ('uuid', 'nome', 'versao', 'tipo_incidente')
        }),
        ('Procedimentos', {
            'fields': (
                'procedimento_preparacao', 'procedimento_identificacao',
                'procedimento_contencao', 'procedimento_erradicacao',
                'procedimento_recuperacao', 'procedimento_licoes'
            )
        }),
        ('Equipe', {
            'fields': ('equipe_resposta', 'contatos_emergencia')
        }),
        ('Aprovação', {
            'fields': ('aprovado_por', 'data_aprovacao', 'proxima_revisao')
        }),
        ('Metadados', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )


@admin.register(AcaoResposta)
class AcaoRespostaAdmin(admin.ModelAdmin):
    list_display = [
        'incidente', 'tipo', 'executado_por',
        'data_inicio', 'data_conclusao', 'is_active'
    ]
    list_filter = ['tipo', 'is_active', 'created_at']
    search_fields = ['descricao', 'resultado']
    readonly_fields = ['created_at', 'updated_at', 'uuid']
    raw_id_fields = ['incidente', 'executado_por']
    
    fieldsets = (
        ('Identificação', {
            'fields': ('uuid', 'incidente', 'tipo', 'descricao')
        }),
        ('Execução', {
            'fields': ('executado_por', 'data_inicio', 'data_conclusao')
        }),
        ('Resultado', {
            'fields': ('resultado', 'evidencias')
        }),
        ('Metadados', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )


# ============================================
# RECOVER (RC) - Recuperar
# ============================================

@admin.register(PlanoRecuperacao)
class PlanoRecuperacaoAdmin(admin.ModelAdmin):
    list_display = [
        'nome', 'versao', 'rto', 'rpo',
        'ultimo_teste', 'proximo_teste', 'testado_recentemente'
    ]
    list_filter = ['is_active']
    search_fields = ['nome', 'site_contingencia']
    readonly_fields = ['created_at', 'updated_at', 'uuid']
    raw_id_fields = ['aprovado_por']
    
    fieldsets = (
        ('Identificação', {
            'fields': ('uuid', 'nome', 'versao')
        }),
        ('Objetivos', {
            'fields': ('rto', 'rpo')
        }),
        ('Sistemas', {
            'fields': ('sistemas_criticos',)
        }),
        ('Procedimentos', {
            'fields': ('procedimentos_recuperacao', 'ordem_recuperacao')
        }),
        ('Recursos', {
            'fields': ('recursos_necessarios', 'site_contingencia')
        }),
        ('Testes', {
            'fields': ('ultimo_teste', 'resultado_ultimo_teste', 'proximo_teste')
        }),
        ('Aprovação', {
            'fields': ('aprovado_por', 'data_aprovacao')
        }),
        ('Metadados', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )
    
    def testado_recentemente(self, obj):
        if not obj.ultimo_teste:
            return format_html('<span style="color: orange;">Nunca testado</span>')
        
        dias = (timezone.now().date() - obj.ultimo_teste).days
        if dias > 365:
            return format_html('<span style="color: red;">Há {} dias</span>', dias)
        elif dias > 180:
            return format_html('<span style="color: orange;">Há {} dias</span>', dias)
        return format_html('<span style="color: green;">Há {} dias</span>', dias)
    testado_recentemente.short_description = 'Último Teste'


@admin.register(TesteRecuperacao)
class TesteRecuperacaoAdmin(admin.ModelAdmin):
    list_display = [
        'plano', 'tipo', 'data_execucao', 'sucesso',
        'rto_alcancado', 'rpo_alcancado', 'coordenado_por'
    ]
    list_filter = ['tipo', 'sucesso', 'created_at']
    search_fields = ['cenario', 'licoes_aprendidas']
    readonly_fields = ['created_at', 'updated_at', 'uuid']
    raw_id_fields = ['plano', 'coordenado_por']
    
    fieldsets = (
        ('Identificação', {
            'fields': ('uuid', 'plano', 'tipo')
        }),
        ('Execução', {
            'fields': ('data_execucao', 'participantes', 'coordenado_por')
        }),
        ('Cenário', {
            'fields': ('cenario',)
        }),
        ('Resultados', {
            'fields': ('sucesso', 'rto_alcancado', 'rpo_alcancado')
        }),
        ('Aprendizados', {
            'fields': ('problemas_identificados', 'licoes_aprendidas', 'acoes_melhoria')
        }),
        ('Metadados', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )


@admin.register(BackupRegistro)
class BackupRegistroAdmin(admin.ModelAdmin):
    list_display = [
        'ativo', 'tipo', 'data_inicio', 'sucesso',
        'tamanho_display', 'verificado', 'criptografado'
    ]
    list_filter = ['tipo', 'sucesso', 'verificado', 'criptografado', 'created_at']
    search_fields = ['localizacao']
    readonly_fields = ['created_at', 'updated_at', 'uuid']
    raw_id_fields = ['ativo']
    
    fieldsets = (
        ('Identificação', {
            'fields': ('uuid', 'ativo', 'tipo')
        }),
        ('Execução', {
            'fields': ('data_inicio', 'data_conclusao', 'sucesso')
        }),
        ('Detalhes', {
            'fields': ('tamanho_bytes', 'localizacao')
        }),
        ('Verificação', {
            'fields': ('verificado', 'data_verificacao')
        }),
        ('Retenção', {
            'fields': ('data_expiracao',)
        }),
        ('Segurança', {
            'fields': ('criptografado', 'algoritmo_criptografia')
        }),
        ('Metadados', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )
    
    def tamanho_display(self, obj):
        if not obj.tamanho_bytes:
            return '-'
        
        gb = obj.tamanho_bytes / (1024**3)
        if gb >= 1:
            return f'{gb:.2f} GB'
        
        mb = obj.tamanho_bytes / (1024**2)
        if mb >= 1:
            return f'{mb:.2f} MB'
        
        kb = obj.tamanho_bytes / 1024
        return f'{kb:.2f} KB'
    tamanho_display.short_description = 'Tamanho'
