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
        'nome', 'tipo', 'classificacao', 'criticidade',
        'departamento_responsavel', 'status', 'created_at'
    ]
    list_filter = ['tipo', 'classificacao', 'criticidade', 'status']
    search_fields = ['nome', 'descricao', 'codigo_identificacao']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Identificação', {
            'fields': ('codigo_identificacao', 'nome', 'descricao', 'tipo')
        }),
        ('Classificação', {
            'fields': ('classificacao', 'criticidade', 'valor_estimado')
        }),
        ('Responsabilidade', {
            'fields': ('departamento_responsavel', 'proprietario', 'custodiante')
        }),
        ('Localização', {
            'fields': ('localizacao_fisica', 'localizacao_logica', 'ambiente')
        }),
        ('Conformidade', {
            'fields': ('requisitos_conformidade', 'dados_pessoais', 'dados_sensiveis')
        }),
        ('Status', {
            'fields': ('status', 'data_aquisicao', 'data_descarte')
        }),
    )


@admin.register(AvaliacaoRisco)
class AvaliacaoRiscoAdmin(admin.ModelAdmin):
    list_display = [
        'ativo', 'ameaca', 'probabilidade', 'impacto',
        'score_risco_display', 'nivel_risco', 'status'
    ]
    list_filter = ['nivel_risco', 'status', 'created_at']
    search_fields = ['ameaca', 'vulnerabilidade']
    readonly_fields = ['score_risco', 'nivel_risco', 'created_at', 'updated_at']
    raw_id_fields = ['ativo', 'avaliador']
    
    fieldsets = (
        ('Ativo e Ameaça', {
            'fields': ('ativo', 'ameaca', 'vulnerabilidade', 'cenario_risco')
        }),
        ('Avaliação', {
            'fields': ('probabilidade', 'impacto', 'score_risco', 'nivel_risco')
        }),
        ('Tratamento', {
            'fields': ('estrategia_tratamento', 'controles_existentes', 'controles_propostos')
        }),
        ('Risco Residual', {
            'fields': ('probabilidade_residual', 'impacto_residual', 
                      'score_residual', 'nivel_residual')
        }),
        ('Responsabilidade', {
            'fields': ('avaliador', 'responsavel_tratamento', 'prazo_tratamento')
        }),
        ('Status', {
            'fields': ('status', 'justificativa_aceitacao')
        }),
    )
    
    def score_risco_display(self, obj):
        score = obj.score_risco
        if score >= 20:
            color = 'red'
        elif score >= 13:
            color = 'orange'
        elif score >= 9:
            color = 'yellow'
        else:
            color = 'green'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}/25</span>',
            color, score
        )
    score_risco_display.short_description = 'Score'


# ============================================
# PROTECT (PR) - Proteger
# ============================================

@admin.register(ControleAcesso)
class ControleAcessoAdmin(admin.ModelAdmin):
    list_display = [
        'nome', 'tipo_controle', 'escopo', 'criticidade',
        'ativo', 'automatizado'
    ]
    list_filter = ['tipo_controle', 'escopo', 'criticidade', 'ativo']
    search_fields = ['nome', 'descricao']
    
    fieldsets = (
        ('Identificação', {
            'fields': ('nome', 'descricao', 'tipo_controle')
        }),
        ('Aplicação', {
            'fields': ('escopo', 'sistemas_aplicados', 'grupos_aplicados')
        }),
        ('Configuração', {
            'fields': ('criticidade', 'automatizado', 'reversivel')
        }),
        ('Política', {
            'fields': ('politica_relacionada', 'procedimento_operacional')
        }),
        ('Status', {
            'fields': ('ativo', 'data_implementacao', 'data_ultima_revisao')
        }),
    )


@admin.register(ConfiguracaoSeguranca)
class ConfiguracaoSegurancaAdmin(admin.ModelAdmin):
    list_display = [
        'sistema', 'ambiente', 'conformidade_status',
        'em_conformidade', 'ultima_verificacao'
    ]
    list_filter = ['ambiente', 'em_conformidade', 'criticidade']
    search_fields = ['sistema', 'versao']
    raw_id_fields = ['responsavel']
    
    def conformidade_status(self, obj):
        if obj.em_conformidade:
            return format_html('<span style="color: green;">✓ Conforme</span>')
        return format_html('<span style="color: red;">✗ Não Conforme</span>')
    conformidade_status.short_description = 'Conformidade'


@admin.register(TreinamentoSeguranca)
class TreinamentoSegurancaAdmin(admin.ModelAdmin):
    list_display = [
        'titulo', 'tipo', 'carga_horaria', 'obrigatorio',
        'status', 'participantes_count'
    ]
    list_filter = ['tipo', 'obrigatorio', 'status']
    search_fields = ['titulo', 'descricao']
    
    def participantes_count(self, obj):
        return len(obj.participantes) if obj.participantes else 0
    participantes_count.short_description = 'Participantes'


# ============================================
# DETECT (DE) - Detectar
# ============================================

@admin.register(RegraDeteccao)
class RegraDeteccaoAdmin(admin.ModelAdmin):
    list_display = [
        'nome', 'tipo_evento', 'severidade', 'ativa',
        'total_acionamentos'
    ]
    list_filter = ['tipo_evento', 'severidade', 'ativa']
    search_fields = ['nome', 'descricao']
    
    fieldsets = (
        ('Identificação', {
            'fields': ('nome', 'descricao', 'tipo_evento')
        }),
        ('Condições', {
            'fields': ('condicoes', 'limiar', 'janela_tempo_segundos')
        }),
        ('Resposta', {
            'fields': ('severidade', 'acoes_automaticas')
        }),
        ('Status', {
            'fields': ('ativa', 'total_acionamentos', 'ultimo_acionamento')
        }),
    )


@admin.register(AlertaSeguranca)
class AlertaSegurancaAdmin(admin.ModelAdmin):
    list_display = [
        'titulo', 'regra', 'severidade_display', 'status',
        'atribuido_para', 'created_at'
    ]
    list_filter = ['severidade', 'status', 'created_at']
    search_fields = ['titulo', 'descricao', 'origem']
    readonly_fields = ['created_at']
    raw_id_fields = ['regra', 'atribuido_para', 'resolvido_por']
    
    def severidade_display(self, obj):
        cores = {
            'informativo': 'blue',
            'baixa': 'green',
            'media': 'yellow',
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
        'nome', 'tipo_incidente', 'severidade', 'status',
        'data_ultima_revisao'
    ]
    list_filter = ['tipo_incidente', 'severidade', 'status']
    search_fields = ['nome', 'descricao']


@admin.register(AcaoResposta)
class AcaoRespostaAdmin(admin.ModelAdmin):
    list_display = [
        'titulo', 'incidente', 'tipo_acao', 'prioridade',
        'status', 'responsavel'
    ]
    list_filter = ['tipo_acao', 'prioridade', 'status']
    search_fields = ['titulo', 'descricao']
    raw_id_fields = ['incidente', 'plano', 'responsavel']


# ============================================
# RECOVER (RC) - Recuperar
# ============================================

@admin.register(PlanoRecuperacao)
class PlanoRecuperacaoAdmin(admin.ModelAdmin):
    list_display = [
        'nome', 'tipo_desastre', 'criticidade', 'status',
        'rto_horas', 'rpo_horas', 'testado_recentemente'
    ]
    list_filter = ['tipo_desastre', 'criticidade', 'status']
    search_fields = ['nome', 'descricao']
    
    def testado_recentemente(self, obj):
        if not obj.data_ultimo_teste:
            return format_html('<span style="color: orange;">Nunca testado</span>')
        
        dias = (timezone.now().date() - obj.data_ultimo_teste).days
        if dias > 365:
            return format_html('<span style="color: red;">Há {} dias</span>', dias)
        elif dias > 180:
            return format_html('<span style="color: orange;">Há {} dias</span>', dias)
        return format_html('<span style="color: green;">Há {} dias</span>', dias)
    testado_recentemente.short_description = 'Último Teste'


@admin.register(TesteRecuperacao)
class TesteRecuperacaoAdmin(admin.ModelAdmin):
    list_display = [
        'plano', 'cenario', 'resultado', 'testado_por', 'created_at'
    ]
    list_filter = ['resultado', 'created_at']
    search_fields = ['cenario', 'observacoes']
    raw_id_fields = ['plano', 'testado_por']


@admin.register(BackupRegistro)
class BackupRegistroAdmin(admin.ModelAdmin):
    list_display = [
        'nome', 'tipo', 'sistema', 'tamanho_display',
        'verificado', 'integridade_ok', 'created_at'
    ]
    list_filter = ['tipo', 'verificado', 'integridade_ok', 'created_at']
    search_fields = ['nome', 'sistema', 'localizacao']
    readonly_fields = ['created_at']
    
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
