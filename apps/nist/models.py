"""
SyncRH - Conformidade NIST Cybersecurity Framework
==================================================
Implementação dos controles do NIST CSF (Identify, Protect, Detect, Respond, Recover)

Este módulo implementa:
- Identificação de Ativos e Riscos
- Proteção de Dados e Sistemas
- Detecção de Ameaças
- Resposta a Incidentes
- Recuperação de Desastres
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


class BaseModel(models.Model):
    """Modelo base"""
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


# =============================================================================
# IDENTIFY (ID) - Identificação
# =============================================================================

class AtivoInformacao(BaseModel):
    """
    Inventário de Ativos de Informação (ID.AM-1, ID.AM-2)
    """
    
    TIPOS = [
        ('dados', 'Dados/Informações'),
        ('software', 'Software/Aplicação'),
        ('hardware', 'Hardware'),
        ('rede', 'Infraestrutura de Rede'),
        ('pessoas', 'Pessoas/Conhecimento'),
        ('servico', 'Serviço'),
    ]
    
    CLASSIFICACOES = [
        ('publico', 'Público'),
        ('interno', 'Interno'),
        ('confidencial', 'Confidencial'),
        ('restrito', 'Restrito'),
    ]
    
    nome = models.CharField(max_length=200)
    descricao = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPOS)
    classificacao = models.CharField(max_length=20, choices=CLASSIFICACOES)
    
    # Localização
    localizacao = models.CharField(max_length=200)
    ambiente = models.CharField(
        max_length=20,
        choices=[
            ('producao', 'Produção'),
            ('homologacao', 'Homologação'),
            ('desenvolvimento', 'Desenvolvimento'),
        ]
    )
    
    # Proprietário e custodiante
    proprietario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='ativos_proprietario'
    )
    custodiante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='ativos_custodiante'
    )
    
    # Valor e criticidade
    valor_negocio = models.CharField(
        max_length=20,
        choices=[
            ('baixo', 'Baixo'),
            ('medio', 'Médio'),
            ('alto', 'Alto'),
            ('critico', 'Crítico'),
        ]
    )
    
    # Dependências
    dependencias = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='dependentes'
    )
    
    class Meta:
        verbose_name = 'Ativo de Informação'
        verbose_name_plural = 'Ativos de Informação'
    
    def __str__(self):
        return f"{self.nome} ({self.get_classificacao_display()})"


class AvaliacaoRisco(BaseModel):
    """
    Avaliação de Riscos (ID.RA)
    """
    
    STATUS_CHOICES = [
        ('identificado', 'Identificado'),
        ('analisado', 'Analisado'),
        ('tratado', 'Tratado'),
        ('aceito', 'Aceito'),
        ('monitorado', 'Monitorado'),
    ]
    
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    
    # Ativo relacionado
    ativo = models.ForeignKey(
        AtivoInformacao,
        on_delete=models.CASCADE,
        related_name='riscos'
    )
    
    # Análise de risco
    ameaca = models.CharField(max_length=200)
    vulnerabilidade = models.CharField(max_length=200)
    
    # Probabilidade e Impacto (matriz 5x5)
    probabilidade = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)],
        help_text='1=Raro, 2=Improvável, 3=Possível, 4=Provável, 5=Quase Certo'
    )
    impacto = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)],
        help_text='1=Insignificante, 2=Menor, 3=Moderado, 4=Maior, 5=Catastrófico'
    )
    
    # Cálculo do risco
    @property
    def nivel_risco(self):
        return self.probabilidade * self.impacto
    
    @property
    def classificacao_risco(self):
        nivel = self.nivel_risco
        if nivel <= 4:
            return 'baixo'
        elif nivel <= 9:
            return 'medio'
        elif nivel <= 16:
            return 'alto'
        return 'critico'
    
    # Tratamento
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='identificado')
    estrategia_tratamento = models.CharField(
        max_length=20,
        choices=[
            ('mitigar', 'Mitigar'),
            ('transferir', 'Transferir'),
            ('aceitar', 'Aceitar'),
            ('evitar', 'Evitar'),
        ],
        blank=True
    )
    plano_acao = models.TextField(blank=True)
    
    # Risco residual
    risco_residual = models.IntegerField(null=True, blank=True)
    
    # Responsável
    responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    data_revisao = models.DateField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Avaliação de Risco'
        verbose_name_plural = 'Avaliações de Risco'
    
    def __str__(self):
        return f"{self.titulo} - Nível: {self.nivel_risco}"


# =============================================================================
# PROTECT (PR) - Proteção
# =============================================================================

class ControleAcesso(BaseModel):
    """
    Registro de Controles de Acesso (PR.AC)
    """
    
    ativo = models.ForeignKey(
        AtivoInformacao,
        on_delete=models.CASCADE,
        related_name='controles_acesso'
    )
    
    # Tipo de controle
    tipo = models.CharField(
        max_length=30,
        choices=[
            ('autenticacao', 'Autenticação'),
            ('autorizacao', 'Autorização'),
            ('segregacao', 'Segregação de Funções'),
            ('revisao_acesso', 'Revisão de Acesso'),
            ('gestao_privilegio', 'Gestão de Privilégios'),
        ]
    )
    
    descricao = models.TextField()
    
    # Configuração
    requisitos = models.JSONField(default=list)
    implementacao = models.TextField()
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('planejado', 'Planejado'),
            ('implementado', 'Implementado'),
            ('em_revisao', 'Em Revisão'),
            ('desativado', 'Desativado'),
        ],
        default='implementado'
    )
    
    # Efetividade
    ultima_verificacao = models.DateTimeField(null=True, blank=True)
    efetividade = models.CharField(
        max_length=20,
        choices=[
            ('efetivo', 'Efetivo'),
            ('parcial', 'Parcialmente Efetivo'),
            ('inefetivo', 'Inefetivo'),
        ],
        blank=True
    )
    
    class Meta:
        verbose_name = 'Controle de Acesso'
        verbose_name_plural = 'Controles de Acesso'
    
    def __str__(self):
        return f"{self.ativo.nome} - {self.get_tipo_display()}"


class ConfiguracaoSeguranca(BaseModel):
    """
    Baseline de Configuração Segura (PR.IP-1)
    """
    
    nome = models.CharField(max_length=200)
    tipo_sistema = models.CharField(
        max_length=50,
        choices=[
            ('servidor', 'Servidor'),
            ('aplicacao', 'Aplicação'),
            ('banco_dados', 'Banco de Dados'),
            ('rede', 'Dispositivo de Rede'),
            ('estacao', 'Estação de Trabalho'),
            ('container', 'Container'),
            ('cloud', 'Serviço Cloud'),
        ]
    )
    
    # Configurações
    configuracoes = models.JSONField(
        default=dict,
        help_text='Configurações de segurança em formato JSON'
    )
    
    # Versão e validade
    versao = models.CharField(max_length=20)
    data_aprovacao = models.DateField()
    proxima_revisao = models.DateField()
    
    # Compliance
    frameworks = models.JSONField(
        default=list,
        help_text='Frameworks de referência (CIS, NIST, etc.)'
    )
    
    class Meta:
        verbose_name = 'Configuração de Segurança'
        verbose_name_plural = 'Configurações de Segurança'
    
    def __str__(self):
        return f"{self.nome} v{self.versao}"


class TreinamentoSeguranca(BaseModel):
    """
    Registro de Treinamentos de Segurança (PR.AT)
    """
    
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    
    tipo = models.CharField(
        max_length=30,
        choices=[
            ('conscientizacao', 'Conscientização'),
            ('tecnico', 'Técnico'),
            ('phishing', 'Simulação de Phishing'),
            ('incidentes', 'Resposta a Incidentes'),
            ('privacidade', 'Privacidade de Dados'),
        ]
    )
    
    # Público-alvo
    obrigatorio = models.BooleanField(default=False)
    publico_alvo = models.JSONField(default=list)
    
    # Execução
    carga_horaria = models.IntegerField(help_text='Duração em minutos')
    validade_dias = models.IntegerField(default=365)
    
    class Meta:
        verbose_name = 'Treinamento de Segurança'
        verbose_name_plural = 'Treinamentos de Segurança'
    
    def __str__(self):
        return self.titulo


# =============================================================================
# DETECT (DE) - Detecção
# =============================================================================

class RegraDeteccao(BaseModel):
    """
    Regras de Detecção de Anomalias (DE.AE, DE.CM)
    """
    
    nome = models.CharField(max_length=200)
    descricao = models.TextField()
    
    tipo = models.CharField(
        max_length=30,
        choices=[
            ('comportamento', 'Análise de Comportamento'),
            ('assinatura', 'Baseado em Assinatura'),
            ('anomalia', 'Detecção de Anomalia'),
            ('correlacao', 'Correlação de Eventos'),
        ]
    )
    
    # Configuração da regra
    condicoes = models.JSONField(
        default=dict,
        help_text='Condições para ativação da regra'
    )
    severidade = models.CharField(
        max_length=20,
        choices=[
            ('info', 'Informativo'),
            ('baixa', 'Baixa'),
            ('media', 'Média'),
            ('alta', 'Alta'),
            ('critica', 'Crítica'),
        ]
    )
    
    # Ações automáticas
    acoes = models.JSONField(
        default=list,
        help_text='Ações a executar quando ativada'
    )
    
    # Status
    habilitada = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Regra de Detecção'
        verbose_name_plural = 'Regras de Detecção'
    
    def __str__(self):
        return f"{self.nome} ({self.get_severidade_display()})"


class AlertaSeguranca(BaseModel):
    """
    Alertas de Segurança Detectados (DE.AE-2)
    """
    
    STATUS_CHOICES = [
        ('novo', 'Novo'),
        ('triagem', 'Em Triagem'),
        ('investigacao', 'Em Investigação'),
        ('falso_positivo', 'Falso Positivo'),
        ('confirmado', 'Confirmado'),
        ('resolvido', 'Resolvido'),
    ]
    
    regra = models.ForeignKey(
        RegraDeteccao,
        on_delete=models.SET_NULL,
        null=True,
        related_name='alertas'
    )
    
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    severidade = models.CharField(
        max_length=20,
        choices=[
            ('baixa', 'Baixa'),
            ('media', 'Média'),
            ('alta', 'Alta'),
            ('critica', 'Crítica'),
        ]
    )
    
    # Detalhes do alerta
    fonte = models.CharField(max_length=100)
    dados_evento = models.JSONField(default=dict)
    
    # Afetados
    usuarios_afetados = models.JSONField(default=list)
    ativos_afetados = models.ManyToManyField(AtivoInformacao, blank=True)
    
    # Status e tratamento
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='novo')
    atribuido_para = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # Resolução
    analise = models.TextField(blank=True)
    data_resolucao = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Alerta de Segurança'
        verbose_name_plural = 'Alertas de Segurança'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.titulo} - {self.get_status_display()}"


# =============================================================================
# RESPOND (RS) - Resposta
# =============================================================================

class PlanoRespostaIncidente(BaseModel):
    """
    Plano de Resposta a Incidentes (RS.RP)
    """
    
    nome = models.CharField(max_length=200)
    versao = models.CharField(max_length=20)
    
    tipo_incidente = models.CharField(
        max_length=50,
        choices=[
            ('malware', 'Malware'),
            ('phishing', 'Phishing'),
            ('vazamento', 'Vazamento de Dados'),
            ('ddos', 'DDoS'),
            ('acesso_nao_autorizado', 'Acesso Não Autorizado'),
            ('ransomware', 'Ransomware'),
            ('engenharia_social', 'Engenharia Social'),
            ('geral', 'Geral'),
        ]
    )
    
    # Procedimentos por fase
    procedimento_preparacao = models.TextField()
    procedimento_identificacao = models.TextField()
    procedimento_contencao = models.TextField()
    procedimento_erradicacao = models.TextField()
    procedimento_recuperacao = models.TextField()
    procedimento_licoes = models.TextField()
    
    # Equipe de resposta
    equipe_resposta = models.JSONField(
        default=list,
        help_text='Membros da equipe e seus papéis'
    )
    
    # Contatos
    contatos_emergencia = models.JSONField(default=list)
    
    # Aprovação
    aprovado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    data_aprovacao = models.DateField(null=True, blank=True)
    proxima_revisao = models.DateField()
    
    class Meta:
        verbose_name = 'Plano de Resposta a Incidentes'
        verbose_name_plural = 'Planos de Resposta a Incidentes'
    
    def __str__(self):
        return f"{self.nome} v{self.versao}"


class AcaoResposta(BaseModel):
    """
    Ações de Resposta Executadas (RS.MI, RS.AN)
    """
    
    incidente = models.ForeignKey(
        'lgpd.IncidenteSeguranca',
        on_delete=models.CASCADE,
        related_name='acoes_resposta'
    )
    
    tipo = models.CharField(
        max_length=30,
        choices=[
            ('contencao', 'Contenção'),
            ('erradicacao', 'Erradicação'),
            ('recuperacao', 'Recuperação'),
            ('comunicacao', 'Comunicação'),
            ('forense', 'Análise Forense'),
        ]
    )
    
    descricao = models.TextField()
    
    # Execução
    executado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    data_inicio = models.DateTimeField()
    data_conclusao = models.DateTimeField(null=True, blank=True)
    
    # Resultado
    resultado = models.TextField(blank=True)
    evidencias = models.JSONField(default=list)
    
    class Meta:
        verbose_name = 'Ação de Resposta'
        verbose_name_plural = 'Ações de Resposta'
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.descricao[:50]}"


# =============================================================================
# RECOVER (RC) - Recuperação
# =============================================================================

class PlanoRecuperacao(BaseModel):
    """
    Plano de Recuperação de Desastres (RC.RP)
    """
    
    nome = models.CharField(max_length=200)
    versao = models.CharField(max_length=20)
    
    # Objetivos
    rto = models.IntegerField(
        help_text='Recovery Time Objective em horas'
    )
    rpo = models.IntegerField(
        help_text='Recovery Point Objective em horas'
    )
    
    # Sistemas cobertos
    sistemas_criticos = models.ManyToManyField(
        AtivoInformacao,
        related_name='planos_recuperacao'
    )
    
    # Procedimentos
    procedimentos_recuperacao = models.TextField()
    ordem_recuperacao = models.JSONField(
        default=list,
        help_text='Ordem de prioridade para recuperação'
    )
    
    # Recursos necessários
    recursos_necessarios = models.JSONField(default=list)
    site_contingencia = models.CharField(max_length=200, blank=True)
    
    # Testes
    ultimo_teste = models.DateField(null=True, blank=True)
    resultado_ultimo_teste = models.TextField(blank=True)
    proximo_teste = models.DateField()
    
    # Aprovação
    aprovado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    data_aprovacao = models.DateField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Plano de Recuperação'
        verbose_name_plural = 'Planos de Recuperação'
    
    def __str__(self):
        return f"{self.nome} v{self.versao}"


class TesteRecuperacao(BaseModel):
    """
    Registro de Testes de Recuperação (RC.IM)
    """
    
    plano = models.ForeignKey(
        PlanoRecuperacao,
        on_delete=models.CASCADE,
        related_name='testes'
    )
    
    tipo = models.CharField(
        max_length=30,
        choices=[
            ('tabletop', 'Exercício de Mesa'),
            ('walkthrough', 'Walkthrough'),
            ('simulacao', 'Simulação'),
            ('paralelo', 'Teste Paralelo'),
            ('completo', 'Teste Completo'),
        ]
    )
    
    data_execucao = models.DateTimeField()
    participantes = models.JSONField(default=list)
    
    # Cenário testado
    cenario = models.TextField()
    
    # Resultados
    rto_alcancado = models.IntegerField(
        null=True,
        blank=True,
        help_text='RTO real em horas'
    )
    rpo_alcancado = models.IntegerField(
        null=True,
        blank=True,
        help_text='RPO real em horas'
    )
    
    sucesso = models.BooleanField(default=False)
    problemas_identificados = models.JSONField(default=list)
    licoes_aprendidas = models.TextField(blank=True)
    acoes_melhoria = models.JSONField(default=list)
    
    # Responsável
    coordenado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    
    class Meta:
        verbose_name = 'Teste de Recuperação'
        verbose_name_plural = 'Testes de Recuperação'
    
    def __str__(self):
        status = 'Sucesso' if self.sucesso else 'Falha'
        return f"{self.plano.nome} - {self.data_execucao.date()} ({status})"


class BackupRegistro(BaseModel):
    """
    Registro de Backups (RC.CO)
    """
    
    ativo = models.ForeignKey(
        AtivoInformacao,
        on_delete=models.CASCADE,
        related_name='backups'
    )
    
    tipo = models.CharField(
        max_length=20,
        choices=[
            ('completo', 'Completo'),
            ('incremental', 'Incremental'),
            ('diferencial', 'Diferencial'),
        ]
    )
    
    # Execução
    data_inicio = models.DateTimeField()
    data_conclusao = models.DateTimeField(null=True, blank=True)
    sucesso = models.BooleanField(default=False)
    
    # Detalhes
    tamanho_bytes = models.BigIntegerField(null=True, blank=True)
    localizacao = models.CharField(max_length=500)
    
    # Verificação
    verificado = models.BooleanField(default=False)
    data_verificacao = models.DateTimeField(null=True, blank=True)
    
    # Retenção
    data_expiracao = models.DateField()
    
    # Criptografia
    criptografado = models.BooleanField(default=True)
    algoritmo_criptografia = models.CharField(max_length=50, default='AES-256')
    
    class Meta:
        verbose_name = 'Registro de Backup'
        verbose_name_plural = 'Registros de Backup'
        ordering = ['-data_inicio']
    
    def __str__(self):
        status = 'OK' if self.sucesso else 'FALHA'
        return f"{self.ativo.nome} - {self.data_inicio.date()} ({status})"
