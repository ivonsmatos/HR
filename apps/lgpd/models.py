"""
SyncRH - Módulo de Conformidade LGPD
====================================
Implementação dos requisitos da Lei Geral de Proteção de Dados (Lei 13.709/2018)

Este módulo implementa:
- Registro de Tratamento de Dados (Art. 37)
- Gestão de Consentimento (Art. 7-11)
- Direitos dos Titulares (Art. 17-22)
- Anonimização e Pseudonimização
- Relatório de Impacto (RIPD)
- Notificação de Incidentes (Art. 48)
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import uuid
import hashlib


class BaseModel(models.Model):
    """Modelo base com campos comuns"""
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


# =============================================================================
# REGISTRO DE OPERAÇÕES DE TRATAMENTO (Art. 37 LGPD)
# =============================================================================

class RegistroTratamento(BaseModel):
    """
    Registro das operações de tratamento de dados pessoais.
    Obrigatório conforme Art. 37 da LGPD.
    """
    
    BASES_LEGAIS = [
        ('consentimento', 'Consentimento do Titular (Art. 7, I)'),
        ('obrigacao_legal', 'Cumprimento de Obrigação Legal (Art. 7, II)'),
        ('administracao_publica', 'Administração Pública (Art. 7, III)'),
        ('estudos_pesquisa', 'Estudos por Órgão de Pesquisa (Art. 7, IV)'),
        ('execucao_contrato', 'Execução de Contrato (Art. 7, V)'),
        ('exercicio_direitos', 'Exercício Regular de Direitos (Art. 7, VI)'),
        ('protecao_vida', 'Proteção da Vida (Art. 7, VII)'),
        ('tutela_saude', 'Tutela da Saúde (Art. 7, VIII)'),
        ('interesse_legitimo', 'Interesse Legítimo (Art. 7, IX)'),
        ('protecao_credito', 'Proteção ao Crédito (Art. 7, X)'),
    ]
    
    FINALIDADES = [
        ('gestao_rh', 'Gestão de Recursos Humanos'),
        ('folha_pagamento', 'Processamento de Folha de Pagamento'),
        ('recrutamento', 'Recrutamento e Seleção'),
        ('treinamento', 'Treinamento e Desenvolvimento'),
        ('avaliacao', 'Avaliação de Desempenho'),
        ('beneficios', 'Gestão de Benefícios'),
        ('saude_seguranca', 'Saúde e Segurança do Trabalho'),
        ('obrigacoes_legais', 'Cumprimento de Obrigações Legais'),
        ('comunicacao', 'Comunicação Interna'),
    ]
    
    nome = models.CharField(max_length=200)
    descricao = models.TextField()
    base_legal = models.CharField(max_length=50, choices=BASES_LEGAIS)
    finalidade = models.CharField(max_length=50, choices=FINALIDADES)
    
    # Categorias de dados tratados
    dados_pessoais = models.JSONField(
        default=list,
        help_text='Lista de categorias de dados pessoais tratados'
    )
    dados_sensiveis = models.JSONField(
        default=list,
        help_text='Lista de dados sensíveis tratados (Art. 5, II)'
    )
    
    # Titulares
    categorias_titulares = models.JSONField(
        default=list,
        help_text='Categorias de titulares (colaboradores, candidatos, etc.)'
    )
    
    # Compartilhamento
    destinatarios = models.JSONField(
        default=list,
        help_text='Organizações com quem dados são compartilhados'
    )
    transferencia_internacional = models.BooleanField(default=False)
    paises_transferencia = models.JSONField(default=list, blank=True)
    
    # Prazo de retenção
    prazo_retencao_dias = models.IntegerField(
        help_text='Prazo de retenção em dias'
    )
    justificativa_retencao = models.TextField()
    
    # Medidas de segurança
    medidas_seguranca = models.JSONField(
        default=list,
        help_text='Medidas técnicas e organizacionais aplicadas'
    )
    
    # Responsáveis
    controlador = models.CharField(max_length=200)
    operador = models.CharField(max_length=200, blank=True)
    encarregado_dpo = models.CharField(max_length=200)
    
    # Status
    aprovado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='registros_aprovados'
    )
    data_aprovacao = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Registro de Tratamento'
        verbose_name_plural = 'Registros de Tratamento'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.nome} - {self.get_finalidade_display()}"


# =============================================================================
# GESTÃO DE CONSENTIMENTO (Art. 7-11 LGPD)
# =============================================================================

class TermoConsentimento(BaseModel):
    """Template de termos de consentimento"""
    
    titulo = models.CharField(max_length=200)
    versao = models.CharField(max_length=20)
    conteudo = models.TextField()
    finalidades = models.JSONField(default=list)
    
    # Vigência
    data_vigencia_inicio = models.DateField()
    data_vigencia_fim = models.DateField(null=True, blank=True)
    
    # Aprovação
    aprovado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    
    class Meta:
        verbose_name = 'Termo de Consentimento'
        verbose_name_plural = 'Termos de Consentimento'
        unique_together = ['titulo', 'versao']
    
    def __str__(self):
        return f"{self.titulo} v{self.versao}"


class ConsentimentoTitular(BaseModel):
    """
    Registro de consentimento dado pelo titular.
    Conforme Art. 8 da LGPD, o consentimento deve ser:
    - Livre, informado e inequívoco
    - Para finalidades determinadas
    - Revogável a qualquer momento
    """
    
    titular = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='consentimentos'
    )
    termo = models.ForeignKey(
        TermoConsentimento,
        on_delete=models.PROTECT,
        related_name='consentimentos'
    )
    
    # Detalhes do consentimento
    finalidades_aceitas = models.JSONField(default=list)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    
    # Timestamps
    data_consentimento = models.DateTimeField(auto_now_add=True)
    data_revogacao = models.DateTimeField(null=True, blank=True)
    motivo_revogacao = models.TextField(blank=True)
    
    # Hash para integridade
    hash_consentimento = models.CharField(max_length=64, editable=False)
    
    class Meta:
        verbose_name = 'Consentimento do Titular'
        verbose_name_plural = 'Consentimentos dos Titulares'
        ordering = ['-data_consentimento']
    
    def save(self, *args, **kwargs):
        if not self.hash_consentimento:
            data = f"{self.titular_id}{self.termo_id}{self.data_consentimento}{self.ip_address}"
            self.hash_consentimento = hashlib.sha256(data.encode()).hexdigest()
        super().save(*args, **kwargs)
    
    def revogar(self, motivo=''):
        """Revoga o consentimento (Art. 8, §5)"""
        self.data_revogacao = timezone.now()
        self.motivo_revogacao = motivo
        self.save()
    
    @property
    def esta_ativo(self):
        return self.data_revogacao is None
    
    def __str__(self):
        status = 'Ativo' if self.esta_ativo else 'Revogado'
        return f"{self.titular} - {self.termo.titulo} ({status})"


# =============================================================================
# DIREITOS DOS TITULARES (Art. 17-22 LGPD)
# =============================================================================

class SolicitacaoTitular(BaseModel):
    """
    Registro de solicitações dos titulares de dados.
    Implementa os direitos previstos no Art. 18 da LGPD.
    """
    
    TIPOS_SOLICITACAO = [
        ('confirmacao', 'Confirmação de Tratamento (Art. 18, I)'),
        ('acesso', 'Acesso aos Dados (Art. 18, II)'),
        ('correcao', 'Correção de Dados (Art. 18, III)'),
        ('anonimizacao', 'Anonimização/Bloqueio/Eliminação (Art. 18, IV)'),
        ('portabilidade', 'Portabilidade dos Dados (Art. 18, V)'),
        ('eliminacao', 'Eliminação de Dados (Art. 18, VI)'),
        ('info_compartilhamento', 'Informação sobre Compartilhamento (Art. 18, VII)'),
        ('info_nao_consentimento', 'Possibilidade de Não Consentir (Art. 18, VIII)'),
        ('revogacao', 'Revogação de Consentimento (Art. 18, IX)'),
        ('oposicao', 'Oposição ao Tratamento (Art. 18, §2)'),
        ('revisao_decisao', 'Revisão de Decisão Automatizada (Art. 20)'),
    ]
    
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('em_analise', 'Em Análise'),
        ('aguardando_info', 'Aguardando Informações'),
        ('em_execucao', 'Em Execução'),
        ('concluida', 'Concluída'),
        ('negada', 'Negada'),
        ('cancelada', 'Cancelada'),
    ]
    
    # Protocolo
    protocolo = models.CharField(max_length=50, unique=True, editable=False)
    
    # Solicitante
    titular = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='solicitacoes_lgpd'
    )
    email_contato = models.EmailField()
    
    # Solicitação
    tipo = models.CharField(max_length=30, choices=TIPOS_SOLICITACAO)
    descricao = models.TextField()
    dados_solicitados = models.JSONField(default=list, blank=True)
    
    # Status e prazos
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    data_limite = models.DateTimeField()  # 15 dias conforme Art. 18, §5
    
    # Resposta
    responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='solicitacoes_atendidas'
    )
    resposta = models.TextField(blank=True)
    data_resposta = models.DateTimeField(null=True, blank=True)
    justificativa_negativa = models.TextField(blank=True)
    
    # Arquivos
    arquivo_resposta = models.FileField(
        upload_to='lgpd/respostas/',
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = 'Solicitação do Titular'
        verbose_name_plural = 'Solicitações dos Titulares'
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.protocolo:
            self.protocolo = f"LGPD{timezone.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6].upper()}"
        if not self.data_limite:
            # 15 dias úteis conforme Art. 18, §5
            self.data_limite = timezone.now() + timedelta(days=21)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.protocolo} - {self.get_tipo_display()}"


# =============================================================================
# ANONIMIZAÇÃO E PSEUDONIMIZAÇÃO
# =============================================================================

class RegistroAnonimizacao(BaseModel):
    """Registro de operações de anonimização de dados"""
    
    TIPOS = [
        ('anonimizacao', 'Anonimização'),
        ('pseudonimizacao', 'Pseudonimização'),
        ('eliminacao', 'Eliminação'),
    ]
    
    tipo = models.CharField(max_length=20, choices=TIPOS)
    motivo = models.CharField(max_length=100)
    descricao = models.TextField()
    
    # Dados afetados
    modelo = models.CharField(max_length=100, help_text='Nome do modelo Django')
    campos = models.JSONField(default=list, help_text='Campos afetados')
    quantidade_registros = models.IntegerField()
    
    # Execução
    executado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    data_execucao = models.DateTimeField(auto_now_add=True)
    
    # Técnica utilizada
    tecnica = models.CharField(max_length=100)
    reversivel = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Registro de Anonimização'
        verbose_name_plural = 'Registros de Anonimização'
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.modelo} ({self.quantidade_registros} registros)"


# =============================================================================
# RELATÓRIO DE IMPACTO À PROTEÇÃO DE DADOS (RIPD)
# =============================================================================

class RelatorioImpacto(BaseModel):
    """
    Relatório de Impacto à Proteção de Dados Pessoais (RIPD).
    Conforme Art. 38 da LGPD.
    """
    
    STATUS_CHOICES = [
        ('rascunho', 'Rascunho'),
        ('em_revisao', 'Em Revisão'),
        ('aprovado', 'Aprovado'),
        ('arquivado', 'Arquivado'),
    ]
    
    titulo = models.CharField(max_length=200)
    versao = models.CharField(max_length=20)
    registro_tratamento = models.ForeignKey(
        RegistroTratamento,
        on_delete=models.CASCADE,
        related_name='relatorios_impacto'
    )
    
    # Descrição do tratamento
    descricao_tratamento = models.TextField()
    necessidade_proporcionalidade = models.TextField()
    
    # Análise de riscos
    riscos_identificados = models.JSONField(default=list)
    probabilidade_risco = models.CharField(
        max_length=20,
        choices=[
            ('baixa', 'Baixa'),
            ('media', 'Média'),
            ('alta', 'Alta'),
        ]
    )
    impacto_risco = models.CharField(
        max_length=20,
        choices=[
            ('baixo', 'Baixo'),
            ('medio', 'Médio'),
            ('alto', 'Alto'),
        ]
    )
    
    # Medidas mitigadoras
    medidas_mitigadoras = models.JSONField(default=list)
    riscos_residuais = models.TextField(blank=True)
    
    # Status e aprovação
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='rascunho')
    elaborado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='ripd_elaborados'
    )
    aprovado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ripd_aprovados'
    )
    data_aprovacao = models.DateTimeField(null=True, blank=True)
    
    # Parecer do DPO
    parecer_dpo = models.TextField(blank=True)
    data_parecer_dpo = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Relatório de Impacto (RIPD)'
        verbose_name_plural = 'Relatórios de Impacto (RIPD)'
    
    def __str__(self):
        return f"{self.titulo} v{self.versao}"


# =============================================================================
# INCIDENTES DE SEGURANÇA (Art. 48 LGPD)
# =============================================================================

class IncidenteSeguranca(BaseModel):
    """
    Registro de incidentes de segurança com dados pessoais.
    Conforme Art. 48 da LGPD, incidentes devem ser comunicados à ANPD.
    """
    
    SEVERIDADES = [
        ('baixa', 'Baixa'),
        ('media', 'Média'),
        ('alta', 'Alta'),
        ('critica', 'Crítica'),
    ]
    
    STATUS_CHOICES = [
        ('detectado', 'Detectado'),
        ('em_investigacao', 'Em Investigação'),
        ('contido', 'Contido'),
        ('erradicado', 'Erradicado'),
        ('recuperado', 'Recuperado'),
        ('fechado', 'Fechado'),
    ]
    
    # Identificação
    protocolo = models.CharField(max_length=50, unique=True, editable=False)
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    
    # Classificação
    severidade = models.CharField(max_length=20, choices=SEVERIDADES)
    tipo_incidente = models.CharField(
        max_length=50,
        choices=[
            ('vazamento', 'Vazamento de Dados'),
            ('acesso_nao_autorizado', 'Acesso Não Autorizado'),
            ('perda_dados', 'Perda de Dados'),
            ('alteracao_indevida', 'Alteração Indevida'),
            ('ransomware', 'Ransomware'),
            ('phishing', 'Phishing'),
            ('outro', 'Outro'),
        ]
    )
    
    # Dados afetados
    dados_afetados = models.JSONField(default=list)
    quantidade_titulares = models.IntegerField(null=True, blank=True)
    categorias_titulares = models.JSONField(default=list)
    
    # Timeline
    data_ocorrencia = models.DateTimeField()
    data_deteccao = models.DateTimeField()
    data_contencao = models.DateTimeField(null=True, blank=True)
    data_resolucao = models.DateTimeField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='detectado')
    
    # Comunicações (Art. 48)
    comunicado_anpd = models.BooleanField(default=False)
    data_comunicacao_anpd = models.DateTimeField(null=True, blank=True)
    protocolo_anpd = models.CharField(max_length=100, blank=True)
    
    comunicado_titulares = models.BooleanField(default=False)
    data_comunicacao_titulares = models.DateTimeField(null=True, blank=True)
    metodo_comunicacao_titulares = models.CharField(max_length=100, blank=True)
    
    # Investigação
    causa_raiz = models.TextField(blank=True)
    acoes_tomadas = models.JSONField(default=list)
    medidas_preventivas = models.JSONField(default=list)
    
    # Responsáveis
    reportado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='incidentes_reportados'
    )
    responsavel_investigacao = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incidentes_investigados'
    )
    
    class Meta:
        verbose_name = 'Incidente de Segurança'
        verbose_name_plural = 'Incidentes de Segurança'
        ordering = ['-data_deteccao']
    
    def save(self, *args, **kwargs):
        if not self.protocolo:
            self.protocolo = f"INC{timezone.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)
    
    @property
    def deve_notificar_anpd(self):
        """Verifica se deve notificar ANPD (prazo razoável)"""
        return self.severidade in ['alta', 'critica'] and not self.comunicado_anpd
    
    def __str__(self):
        return f"{self.protocolo} - {self.titulo}"


# =============================================================================
# LOG DE ACESSO A DADOS PESSOAIS
# =============================================================================

class LogAcessoDados(BaseModel):
    """
    Log de acesso a dados pessoais para auditoria LGPD.
    """
    
    OPERACOES = [
        ('visualizar', 'Visualizar'),
        ('exportar', 'Exportar'),
        ('editar', 'Editar'),
        ('excluir', 'Excluir'),
        ('compartilhar', 'Compartilhar'),
    ]
    
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    
    # Dados acessados
    modelo = models.CharField(max_length=100)
    objeto_id = models.CharField(max_length=100)
    campos_acessados = models.JSONField(default=list)
    
    # Operação
    operacao = models.CharField(max_length=20, choices=OPERACOES)
    finalidade = models.CharField(max_length=200, blank=True)
    
    # Contexto
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    endpoint = models.CharField(max_length=500)
    
    # Timestamp
    data_acesso = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Log de Acesso a Dados'
        verbose_name_plural = 'Logs de Acesso a Dados'
        ordering = ['-data_acesso']
        indexes = [
            models.Index(fields=['usuario', 'data_acesso']),
            models.Index(fields=['modelo', 'objeto_id']),
        ]
    
    def __str__(self):
        return f"{self.usuario} - {self.operacao} - {self.modelo}"
