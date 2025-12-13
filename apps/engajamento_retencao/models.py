"""
Models do Módulo Engajamento e Retenção - SyncRH

Funcionalidades:
- Pesquisa de Clima
- Pesquisa de Satisfação (eNPS)
- Radar de Rotatividade (IA)
- Gestão de Cargos e Salários
- Agente SyncRH (IA para engajamento)
- Benefícios Corporativos
- SuperApp do Colaborador
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class BaseModel(models.Model):
    """Modelo base com campos comuns"""
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        abstract = True


# =====================================================
# PESQUISA DE CLIMA
# =====================================================

class PesquisaClima(BaseModel):
    """Pesquisa de clima organizacional"""
    titulo = models.CharField(max_length=255)
    descricao = models.TextField(blank=True)
    
    # Período
    data_inicio = models.DateField()
    data_fim = models.DateField()
    
    # Configurações
    anonima = models.BooleanField(default=True)
    obrigatoria = models.BooleanField(default=False)
    
    # Escopo
    todos_colaboradores = models.BooleanField(default=True)
    departamentos = models.ManyToManyField('departamento_pessoal.Departamento', blank=True, related_name='pesquisas_clima')
    
    # Status
    status = models.CharField(max_length=30, choices=[
        ('rascunho', 'Rascunho'),
        ('agendada', 'Agendada'),
        ('em_andamento', 'Em Andamento'),
        ('encerrada', 'Encerrada'),
        ('analisada', 'Analisada'),
    ], default='rascunho')
    
    # Resultados
    taxa_participacao = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    score_geral = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    
    # Responsável
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='pesquisas_clima_criadas')
    
    class Meta:
        app_label = 'engajamento_retencao'
        verbose_name = 'Pesquisa de Clima'
        verbose_name_plural = 'Pesquisas de Clima'
        ordering = ['-data_inicio']
    
    def __str__(self):
        return self.titulo


class DimensaoClima(BaseModel):
    """Dimensões avaliadas na pesquisa de clima"""
    pesquisa = models.ForeignKey(PesquisaClima, on_delete=models.CASCADE, related_name='dimensoes')
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    peso = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(10)])
    ordem = models.IntegerField(default=0)
    
    # Resultados
    score_medio = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    
    class Meta:
        app_label = 'engajamento_retencao'
        verbose_name = 'Dimensão de Clima'
        verbose_name_plural = 'Dimensões de Clima'
        ordering = ['ordem']
    
    def __str__(self):
        return f"{self.pesquisa.titulo} - {self.nome}"


class PerguntaClima(BaseModel):
    """Perguntas da pesquisa de clima"""
    dimensao = models.ForeignKey(DimensaoClima, on_delete=models.CASCADE, related_name='perguntas')
    texto = models.TextField()
    tipo = models.CharField(max_length=30, choices=[
        ('escala', 'Escala (1-5)'),
        ('escala_10', 'Escala (1-10)'),
        ('sim_nao', 'Sim/Não'),
        ('multipla', 'Múltipla Escolha'),
        ('aberta', 'Resposta Aberta'),
    ], default='escala')
    obrigatoria = models.BooleanField(default=True)
    opcoes = models.JSONField(default=list, blank=True, help_text='Opções para múltipla escolha')
    ordem = models.IntegerField(default=0)
    
    # Resultados
    media_respostas = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    
    class Meta:
        app_label = 'engajamento_retencao'
        verbose_name = 'Pergunta de Clima'
        verbose_name_plural = 'Perguntas de Clima'
        ordering = ['ordem']
    
    def __str__(self):
        return f"{self.texto[:50]}..."


class RespostaClima(BaseModel):
    """Respostas da pesquisa de clima"""
    pesquisa = models.ForeignKey(PesquisaClima, on_delete=models.CASCADE, related_name='respostas')
    colaborador = models.ForeignKey('departamento_pessoal.Colaborador', on_delete=models.SET_NULL, null=True, blank=True, related_name='respostas_clima')
    
    # Respostas
    respostas = models.JSONField(default=dict, help_text='Dict {pergunta_id: resposta}')
    
    # Metadados
    data_resposta = models.DateTimeField(auto_now_add=True)
    tempo_preenchimento = models.IntegerField(default=0, help_text='Segundos')
    
    class Meta:
        app_label = 'engajamento_retencao'
        verbose_name = 'Resposta de Clima'
        verbose_name_plural = 'Respostas de Clima'
    
    def __str__(self):
        return f"Resposta - {self.pesquisa.titulo}"


class PlanoAcaoClima(BaseModel):
    """Planos de ação baseados nos resultados"""
    pesquisa = models.ForeignKey(PesquisaClima, on_delete=models.CASCADE, related_name='planos_acao')
    dimensao = models.ForeignKey(DimensaoClima, on_delete=models.SET_NULL, null=True, blank=True)
    
    titulo = models.CharField(max_length=255)
    descricao = models.TextField()
    
    # Responsável
    responsavel = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='planos_acao_clima')
    
    # Prazo
    data_inicio = models.DateField()
    data_fim = models.DateField()
    
    # Status
    status = models.CharField(max_length=30, choices=[
        ('planejado', 'Planejado'),
        ('em_andamento', 'Em Andamento'),
        ('concluido', 'Concluído'),
        ('cancelado', 'Cancelado'),
    ], default='planejado')
    
    progresso = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # IA
    sugerido_ia = models.BooleanField(default=False)
    
    class Meta:
        app_label = 'engajamento_retencao'
        verbose_name = 'Plano de Ação (Clima)'
        verbose_name_plural = 'Planos de Ação (Clima)'
    
    def __str__(self):
        return self.titulo


# =====================================================
# PESQUISA DE SATISFAÇÃO (eNPS)
# =====================================================

class PesquisaeNPS(BaseModel):
    """Pesquisa de satisfação eNPS"""
    titulo = models.CharField(max_length=255)
    descricao = models.TextField(blank=True)
    
    # Período
    data_inicio = models.DateField()
    data_fim = models.DateField()
    
    # Pergunta principal
    pergunta_principal = models.TextField(
        default="Em uma escala de 0 a 10, o quanto você recomendaria nossa empresa como um bom lugar para trabalhar?"
    )
    
    # Perguntas adicionais
    perguntas_abertas = models.JSONField(default=list, blank=True)
    
    # Status
    status = models.CharField(max_length=30, choices=[
        ('rascunho', 'Rascunho'),
        ('em_andamento', 'Em Andamento'),
        ('encerrada', 'Encerrada'),
    ], default='rascunho')
    
    # Resultados
    total_respostas = models.IntegerField(default=0)
    promotores = models.IntegerField(default=0)
    neutros = models.IntegerField(default=0)
    detratores = models.IntegerField(default=0)
    score_enps = models.IntegerField(null=True, blank=True, help_text='-100 a 100')
    
    class Meta:
        app_label = 'engajamento_retencao'
        verbose_name = 'Pesquisa eNPS'
        verbose_name_plural = 'Pesquisas eNPS'
        ordering = ['-data_inicio']
    
    def __str__(self):
        return self.titulo
    
    def calcular_enps(self):
        """Calcula o score eNPS"""
        if self.total_respostas > 0:
            pct_promotores = (self.promotores / self.total_respostas) * 100
            pct_detratores = (self.detratores / self.total_respostas) * 100
            self.score_enps = int(pct_promotores - pct_detratores)
            self.save()


class RespostaeNPS(BaseModel):
    """Respostas do eNPS"""
    pesquisa = models.ForeignKey(PesquisaeNPS, on_delete=models.CASCADE, related_name='respostas')
    colaborador = models.ForeignKey('departamento_pessoal.Colaborador', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Nota principal
    nota = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])
    
    # Classificação calculada
    classificacao = models.CharField(max_length=20, choices=[
        ('promotor', 'Promotor (9-10)'),
        ('neutro', 'Neutro (7-8)'),
        ('detrator', 'Detrator (0-6)'),
    ])
    
    # Respostas abertas
    comentarios = models.TextField(blank=True)
    respostas_adicionais = models.JSONField(default=dict, blank=True)
    
    # Metadados
    data_resposta = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'engajamento_retencao'
        verbose_name = 'Resposta eNPS'
        verbose_name_plural = 'Respostas eNPS'
    
    def __str__(self):
        return f"eNPS {self.nota} - {self.classificacao}"
    
    def save(self, *args, **kwargs):
        # Calcula classificação
        if self.nota >= 9:
            self.classificacao = 'promotor'
        elif self.nota >= 7:
            self.classificacao = 'neutro'
        else:
            self.classificacao = 'detrator'
        super().save(*args, **kwargs)


# =====================================================
# RADAR DE ROTATIVIDADE (IA)
# =====================================================

class AnaliseRotatividade(BaseModel):
    """Análise de risco de rotatividade por colaborador"""
    colaborador = models.ForeignKey('departamento_pessoal.Colaborador', on_delete=models.CASCADE, related_name='analises_rotatividade')
    data_analise = models.DateField(auto_now_add=True)
    
    # Score de risco (0-100)
    score_risco = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    classificacao = models.CharField(max_length=20, choices=[
        ('baixo', 'Baixo (0-25)'),
        ('medio', 'Médio (26-50)'),
        ('alto', 'Alto (51-75)'),
        ('critico', 'Crítico (76-100)'),
    ])
    
    # Fatores de risco identificados
    fatores = models.JSONField(default=list, help_text='Lista de fatores que aumentam o risco')
    
    # Indicadores utilizados
    indicadores = models.JSONField(default=dict, help_text='Indicadores que compõem o score')
    
    # Recomendações da IA
    recomendacoes = models.JSONField(default=list)
    
    # Histórico
    score_anterior = models.IntegerField(null=True, blank=True)
    tendencia = models.CharField(max_length=20, choices=[
        ('subindo', 'Subindo ↑'),
        ('estavel', 'Estável →'),
        ('descendo', 'Descendo ↓'),
    ], blank=True)
    
    class Meta:
        app_label = 'engajamento_retencao'
        verbose_name = 'Análise de Rotatividade'
        verbose_name_plural = 'Análises de Rotatividade'
        ordering = ['-data_analise']
    
    def __str__(self):
        return f"{self.colaborador.nome_completo} - Risco: {self.classificacao}"


class AnaliseDemissional(BaseModel):
    """Entrevistas/análises demissionais"""
    colaborador = models.ForeignKey('departamento_pessoal.Colaborador', on_delete=models.CASCADE, related_name='analises_demissionais')
    data_demissao = models.DateField()
    
    # Tipo de desligamento
    tipo = models.CharField(max_length=30, choices=[
        ('voluntaria', 'Demissão Voluntária'),
        ('involuntaria', 'Demissão Involuntária'),
        ('acordo', 'Acordo Mútuo'),
        ('termino_contrato', 'Término de Contrato'),
        ('aposentadoria', 'Aposentadoria'),
    ])
    
    # Motivos
    motivo_principal = models.CharField(max_length=100, choices=[
        ('proposta_melhor', 'Proposta Melhor'),
        ('remuneracao', 'Insatisfação com Remuneração'),
        ('carreira', 'Falta de Crescimento'),
        ('gestao', 'Problemas com Gestão'),
        ('clima', 'Clima Organizacional'),
        ('beneficios', 'Benefícios'),
        ('localizacao', 'Localização/Deslocamento'),
        ('pessoal', 'Motivos Pessoais'),
        ('desempenho', 'Desempenho'),
        ('outros', 'Outros'),
    ], blank=True)
    motivos_detalhados = models.TextField(blank=True)
    
    # Entrevista demissional
    entrevista_realizada = models.BooleanField(default=False)
    data_entrevista = models.DateField(null=True, blank=True)
    entrevistador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Feedback
    recomendaria_empresa = models.BooleanField(null=True, blank=True)
    voltaria_empresa = models.BooleanField(null=True, blank=True)
    nota_experiencia = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(10)])
    
    # Pontos
    pontos_positivos = models.TextField(blank=True)
    pontos_negativos = models.TextField(blank=True)
    sugestoes_melhoria = models.TextField(blank=True)
    
    # Análise IA
    insights_ia = models.JSONField(default=list, blank=True)
    
    class Meta:
        app_label = 'engajamento_retencao'
        verbose_name = 'Análise Demissional'
        verbose_name_plural = 'Análises Demissionais'
        ordering = ['-data_demissao']
    
    def __str__(self):
        return f"{self.colaborador.nome_completo} - {self.data_demissao}"


# =====================================================
# GESTÃO DE CARGOS E SALÁRIOS
# =====================================================

class TabelaSalarial(BaseModel):
    """Tabela salarial da empresa"""
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    data_vigencia = models.DateField()
    
    class Meta:
        app_label = 'engajamento_retencao'
        verbose_name = 'Tabela Salarial'
        verbose_name_plural = 'Tabelas Salariais'
        ordering = ['-data_vigencia']
    
    def __str__(self):
        return f"{self.nome} - Vigência: {self.data_vigencia}"


class FaixaSalarial(BaseModel):
    """Faixas salariais por cargo/nível"""
    tabela = models.ForeignKey(TabelaSalarial, on_delete=models.CASCADE, related_name='faixas')
    cargo = models.ForeignKey('departamento_pessoal.Cargo', on_delete=models.CASCADE, related_name='faixas_salariais')
    
    # Faixa
    salario_minimo = models.DecimalField(max_digits=10, decimal_places=2)
    salario_medio = models.DecimalField(max_digits=10, decimal_places=2)
    salario_maximo = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Steps/níveis dentro da faixa
    steps = models.JSONField(default=list, help_text='Lista de valores de steps')
    
    class Meta:
        app_label = 'engajamento_retencao'
        verbose_name = 'Faixa Salarial'
        verbose_name_plural = 'Faixas Salariais'
        unique_together = ['tabela', 'cargo']
    
    def __str__(self):
        return f"{self.cargo.nome} - R$ {self.salario_minimo} a R$ {self.salario_maximo}"


class PlanoCarreira(BaseModel):
    """Planos de carreira"""
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    
    # Trilha de cargos
    trilha = models.JSONField(default=list, help_text='Lista ordenada de cargos na trilha')
    
    # Requisitos de transição
    requisitos_transicao = models.JSONField(default=dict, help_text='Requisitos para cada transição')
    
    class Meta:
        app_label = 'engajamento_retencao'
        verbose_name = 'Plano de Carreira'
        verbose_name_plural = 'Planos de Carreira'
    
    def __str__(self):
        return self.nome


class SolicitacaoPromocao(BaseModel):
    """Solicitações de promoção/reajuste"""
    colaborador = models.ForeignKey('departamento_pessoal.Colaborador', on_delete=models.CASCADE, related_name='solicitacoes_promocao')
    
    tipo = models.CharField(max_length=30, choices=[
        ('promocao', 'Promoção'),
        ('merito', 'Aumento por Mérito'),
        ('enquadramento', 'Enquadramento'),
        ('reajuste', 'Reajuste'),
    ])
    
    # Valores
    cargo_atual = models.ForeignKey('departamento_pessoal.Cargo', on_delete=models.SET_NULL, null=True, related_name='promocoes_de')
    cargo_proposto = models.ForeignKey('departamento_pessoal.Cargo', on_delete=models.SET_NULL, null=True, blank=True, related_name='promocoes_para')
    salario_atual = models.DecimalField(max_digits=10, decimal_places=2)
    salario_proposto = models.DecimalField(max_digits=10, decimal_places=2)
    percentual_aumento = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Justificativa
    justificativa = models.TextField()
    
    # Aprovações
    status = models.CharField(max_length=30, choices=[
        ('rascunho', 'Rascunho'),
        ('pendente_gestor', 'Pendente Gestor'),
        ('aprovado_gestor', 'Aprovado Gestor'),
        ('pendente_rh', 'Pendente RH'),
        ('aprovado_rh', 'Aprovado RH'),
        ('pendente_diretoria', 'Pendente Diretoria'),
        ('aprovado', 'Aprovado'),
        ('rejeitado', 'Rejeitado'),
        ('efetivado', 'Efetivado'),
    ], default='rascunho')
    
    # Solicitante
    solicitado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='promocoes_solicitadas')
    
    # Datas
    data_efetivacao = models.DateField(null=True, blank=True)
    
    class Meta:
        app_label = 'engajamento_retencao'
        verbose_name = 'Solicitação de Promoção'
        verbose_name_plural = 'Solicitações de Promoção'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.colaborador.nome_completo} - {self.tipo}"


# =====================================================
# BENEFÍCIOS CORPORATIVOS
# =====================================================

class TipoBeneficio(BaseModel):
    """Tipos de benefícios disponíveis"""
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    categoria = models.CharField(max_length=50, choices=[
        ('alimentacao', 'Alimentação'),
        ('transporte', 'Transporte'),
        ('saude', 'Saúde'),
        ('educacao', 'Educação'),
        ('bem_estar', 'Bem-estar'),
        ('financeiro', 'Financeiro'),
        ('outros', 'Outros'),
    ])
    
    # Valores
    valor_padrao = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    valor_desconto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    percentual_desconto = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Fornecedor
    fornecedor = models.CharField(max_length=255, blank=True)
    
    # Configurações
    elegibilidade = models.CharField(max_length=50, choices=[
        ('todos', 'Todos os Colaboradores'),
        ('clt', 'Apenas CLT'),
        ('gestor', 'Apenas Gestores'),
        ('seletivo', 'Seletivo'),
    ], default='todos')
    
    obrigatorio = models.BooleanField(default=False)
    flexivel = models.BooleanField(default=False, help_text='Permite escolha do colaborador')
    
    class Meta:
        app_label = 'engajamento_retencao'
        verbose_name = 'Tipo de Benefício'
        verbose_name_plural = 'Tipos de Benefícios'
    
    def __str__(self):
        return self.nome


class BeneficioColaborador(BaseModel):
    """Benefícios atribuídos a cada colaborador"""
    colaborador = models.ForeignKey('departamento_pessoal.Colaborador', on_delete=models.CASCADE, related_name='beneficios')
    tipo_beneficio = models.ForeignKey(TipoBeneficio, on_delete=models.CASCADE, related_name='atribuicoes')
    
    # Valores
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    valor_desconto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Vigência
    data_inicio = models.DateField()
    data_fim = models.DateField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=30, choices=[
        ('ativo', 'Ativo'),
        ('suspenso', 'Suspenso'),
        ('cancelado', 'Cancelado'),
    ], default='ativo')
    
    # Dependentes (para plano de saúde, etc)
    dependentes = models.JSONField(default=list, blank=True)
    
    observacoes = models.TextField(blank=True)
    
    class Meta:
        app_label = 'engajamento_retencao'
        verbose_name = 'Benefício do Colaborador'
        verbose_name_plural = 'Benefícios dos Colaboradores'
    
    def __str__(self):
        return f"{self.colaborador.nome_completo} - {self.tipo_beneficio.nome}"


# =====================================================
# SUPERAPP DO COLABORADOR
# =====================================================

class NotificacaoColaborador(BaseModel):
    """Notificações para o colaborador no SuperApp"""
    colaborador = models.ForeignKey('departamento_pessoal.Colaborador', on_delete=models.CASCADE, related_name='notificacoes')
    
    titulo = models.CharField(max_length=255)
    mensagem = models.TextField()
    
    tipo = models.CharField(max_length=50, choices=[
        ('info', 'Informação'),
        ('alerta', 'Alerta'),
        ('urgente', 'Urgente'),
        ('lembrete', 'Lembrete'),
        ('parabens', 'Parabéns'),
        ('feedback', 'Feedback'),
        ('ponto', 'Ponto'),
        ('ferias', 'Férias'),
        ('treinamento', 'Treinamento'),
        ('pesquisa', 'Pesquisa'),
    ])
    
    # Link de ação
    link_acao = models.CharField(max_length=255, blank=True)
    
    # Status
    lida = models.BooleanField(default=False)
    data_leitura = models.DateTimeField(null=True, blank=True)
    
    # Expiração
    data_expiracao = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        app_label = 'engajamento_retencao'
        verbose_name = 'Notificação'
        verbose_name_plural = 'Notificações'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.colaborador.nome_completo} - {self.titulo}"


class Reconhecimento(BaseModel):
    """Reconhecimentos entre colaboradores"""
    de_colaborador = models.ForeignKey('departamento_pessoal.Colaborador', on_delete=models.CASCADE, related_name='reconhecimentos_dados')
    para_colaborador = models.ForeignKey('departamento_pessoal.Colaborador', on_delete=models.CASCADE, related_name='reconhecimentos_recebidos')
    
    tipo = models.CharField(max_length=50, choices=[
        ('obrigado', 'Obrigado'),
        ('parabens', 'Parabéns'),
        ('inspiracao', 'Inspiração'),
        ('trabalho_equipe', 'Trabalho em Equipe'),
        ('inovacao', 'Inovação'),
        ('lideranca', 'Liderança'),
        ('ajuda', 'Ajuda'),
    ])
    
    mensagem = models.TextField()
    publico = models.BooleanField(default=True)
    
    # Pontos (gamification)
    pontos = models.IntegerField(default=10)
    
    class Meta:
        app_label = 'engajamento_retencao'
        verbose_name = 'Reconhecimento'
        verbose_name_plural = 'Reconhecimentos'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.de_colaborador.nome_completo} → {self.para_colaborador.nome_completo}: {self.tipo}"


class FeedbackRapido(BaseModel):
    """Feedbacks rápidos entre colaboradores"""
    de_colaborador = models.ForeignKey('departamento_pessoal.Colaborador', on_delete=models.CASCADE, related_name='feedbacks_dados')
    para_colaborador = models.ForeignKey('departamento_pessoal.Colaborador', on_delete=models.CASCADE, related_name='feedbacks_recebidos')
    
    tipo = models.CharField(max_length=30, choices=[
        ('positivo', 'Feedback Positivo'),
        ('construtivo', 'Feedback Construtivo'),
        ('solicitado', 'Feedback Solicitado'),
    ])
    
    conteudo = models.TextField()
    
    # Privacidade
    privado = models.BooleanField(default=True)
    
    # Visualização
    visualizado = models.BooleanField(default=False)
    data_visualizacao = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        app_label = 'engajamento_retencao'
        verbose_name = 'Feedback Rápido'
        verbose_name_plural = 'Feedbacks Rápidos'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Feedback: {self.de_colaborador.nome_completo} → {self.para_colaborador.nome_completo}"


# =====================================================
# AGENTE SYNCRH (IA PARA ENGAJAMENTO)
# =====================================================

class InsightEngajamento(BaseModel):
    """Insights gerados pela IA sobre engajamento"""
    tipo = models.CharField(max_length=50, choices=[
        ('clima', 'Análise de Clima'),
        ('enps', 'Análise eNPS'),
        ('rotatividade', 'Previsão de Rotatividade'),
        ('engajamento', 'Nível de Engajamento'),
        ('padrao', 'Padrão Identificado'),
        ('acao_sugerida', 'Ação Sugerida'),
    ])
    
    # Escopo
    departamento = models.ForeignKey('departamento_pessoal.Departamento', on_delete=models.SET_NULL, null=True, blank=True)
    colaborador = models.ForeignKey('departamento_pessoal.Colaborador', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Conteúdo
    titulo = models.CharField(max_length=255)
    descricao = models.TextField()
    dados_suporte = models.JSONField(default=dict, blank=True)
    
    # Prioridade
    prioridade = models.CharField(max_length=20, choices=[
        ('baixa', 'Baixa'),
        ('media', 'Média'),
        ('alta', 'Alta'),
        ('critica', 'Crítica'),
    ], default='media')
    
    # Ação
    acao_sugerida = models.TextField(blank=True)
    acao_tomada = models.BooleanField(default=False)
    
    class Meta:
        app_label = 'engajamento_retencao'
        verbose_name = 'Insight de Engajamento'
        verbose_name_plural = 'Insights de Engajamento'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.tipo}: {self.titulo}"
