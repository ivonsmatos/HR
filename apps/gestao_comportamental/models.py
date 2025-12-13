"""
Models do Módulo Gestão Comportamental - SyncRH

Funcionalidades:
- Profiler (Análise DISC)
- Engenharia de Cargos (Perfil Comportamental Ideal)
- Matcher (Match entre Perfil e Cargo)
- Métricas do Profiler (Dashboard e Analytics)
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
# PROFILER - ANÁLISE DISC
# =====================================================

class QuestionarioProfiler(BaseModel):
    """Questionários de análise comportamental"""
    titulo = models.CharField(max_length=255)
    descricao = models.TextField(blank=True)
    versao = models.CharField(max_length=20, default='1.0')
    
    # Tipo de questionário
    tipo = models.CharField(max_length=30, choices=[
        ('disc', 'DISC Clássico'),
        ('disc_extendido', 'DISC Estendido'),
        ('big5', 'Big Five'),
        ('mbti', 'MBTI Simplificado'),
        ('personalizado', 'Personalizado'),
    ], default='disc')
    
    # Configurações
    tempo_estimado = models.IntegerField(default=15, help_text='Minutos')
    total_questoes = models.IntegerField(default=24)
    
    # Instruções
    instrucoes = models.TextField(blank=True)
    
    # Publicação
    publicado = models.BooleanField(default=False)
    data_publicacao = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        app_label = 'gestao_comportamental'
        verbose_name = 'Questionário Profiler'
        verbose_name_plural = 'Questionários Profiler'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.titulo} v{self.versao}"


class QuestaoProfiler(BaseModel):
    """Questões do questionário profiler"""
    questionario = models.ForeignKey(QuestionarioProfiler, on_delete=models.CASCADE, related_name='questoes')
    ordem = models.IntegerField(default=0)
    
    # Tipo de questão
    tipo = models.CharField(max_length=30, choices=[
        ('mais_menos', 'Mais/Menos'),  # Escolher o que mais e menos se aplica
        ('ranking', 'Ranking'),  # Ordenar por relevância
        ('escala', 'Escala Likert'),  # Escala de concordância
        ('forcado', 'Escolha Forçada'),  # Escolher entre opções
    ], default='mais_menos')
    
    # Texto da questão (opcional para alguns tipos)
    texto = models.TextField(blank=True)
    
    # Opções (formato depende do tipo)
    opcoes = models.JSONField(default=list, help_text='Lista de opções com mapeamento DISC')
    
    class Meta:
        app_label = 'gestao_comportamental'
        verbose_name = 'Questão Profiler'
        verbose_name_plural = 'Questões Profiler'
        ordering = ['ordem']
    
    def __str__(self):
        return f"Questão {self.ordem} - {self.questionario.titulo}"


class AplicacaoProfiler(BaseModel):
    """Aplicação do profiler para uma pessoa"""
    questionario = models.ForeignKey(QuestionarioProfiler, on_delete=models.CASCADE, related_name='aplicacoes')
    
    # Pode ser colaborador ou candidato
    colaborador = models.ForeignKey('departamento_pessoal.Colaborador', on_delete=models.CASCADE, null=True, blank=True, related_name='aplicacoes_profiler')
    candidato = models.ForeignKey('recrutamento_selecao.Candidato', on_delete=models.CASCADE, null=True, blank=True, related_name='aplicacoes_profiler')
    
    # Status
    status = models.CharField(max_length=30, choices=[
        ('pendente', 'Pendente'),
        ('em_andamento', 'Em Andamento'),
        ('concluido', 'Concluído'),
        ('expirado', 'Expirado'),
    ], default='pendente')
    
    # Datas
    data_envio = models.DateTimeField(auto_now_add=True)
    data_inicio = models.DateTimeField(null=True, blank=True)
    data_conclusao = models.DateTimeField(null=True, blank=True)
    data_expiracao = models.DateTimeField(null=True, blank=True)
    
    # Tempo de resposta
    tempo_total = models.IntegerField(default=0, help_text='Segundos')
    
    # Token de acesso
    token_acesso = models.UUIDField(default=uuid.uuid4, unique=True)
    
    class Meta:
        app_label = 'gestao_comportamental'
        verbose_name = 'Aplicação Profiler'
        verbose_name_plural = 'Aplicações Profiler'
        ordering = ['-data_envio']
    
    def __str__(self):
        pessoa = self.colaborador or self.candidato
        return f"{pessoa} - {self.questionario.titulo}"


class RespostaProfiler(BaseModel):
    """Respostas do profiler"""
    aplicacao = models.ForeignKey(AplicacaoProfiler, on_delete=models.CASCADE, related_name='respostas')
    questao = models.ForeignKey(QuestaoProfiler, on_delete=models.CASCADE, related_name='respostas')
    
    # Resposta (formato depende do tipo de questão)
    resposta = models.JSONField(default=dict)
    
    # Tempo gasto na questão
    tempo_resposta = models.IntegerField(default=0, help_text='Segundos')
    
    class Meta:
        app_label = 'gestao_comportamental'
        verbose_name = 'Resposta Profiler'
        verbose_name_plural = 'Respostas Profiler'
        unique_together = ['aplicacao', 'questao']
    
    def __str__(self):
        return f"Resposta Q{self.questao.ordem} - {self.aplicacao}"


class PerfilDISC(BaseModel):
    """Resultado do perfil DISC calculado"""
    aplicacao = models.OneToOneField(AplicacaoProfiler, on_delete=models.CASCADE, related_name='perfil_disc')
    
    # Scores DISC (0-100)
    dominancia = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], help_text='D - Dominância')
    influencia = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], help_text='I - Influência')
    estabilidade = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], help_text='S - Estabilidade')
    conformidade = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], help_text='C - Conformidade')
    
    # Perfil Natural vs Adaptado
    tipo_perfil = models.CharField(max_length=20, choices=[
        ('natural', 'Perfil Natural'),
        ('adaptado', 'Perfil Adaptado'),
    ], default='natural')
    
    # Perfil Principal (letra dominante)
    perfil_principal = models.CharField(max_length=4, blank=True, help_text='Ex: D, DI, DC, etc.')
    
    # Padrão comportamental
    padrao = models.CharField(max_length=50, blank=True, help_text='Ex: Executor, Comunicador, etc.')
    
    # Características
    pontos_fortes = models.JSONField(default=list)
    areas_desenvolvimento = models.JSONField(default=list)
    estilo_comunicacao = models.TextField(blank=True)
    estilo_lideranca = models.TextField(blank=True)
    ambiente_ideal = models.TextField(blank=True)
    fatores_motivacao = models.JSONField(default=list)
    fatores_desmotivacao = models.JSONField(default=list)
    
    # Confiabilidade do resultado
    indice_consistencia = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    class Meta:
        app_label = 'gestao_comportamental'
        verbose_name = 'Perfil DISC'
        verbose_name_plural = 'Perfis DISC'
    
    def __str__(self):
        return f"{self.perfil_principal} - D:{self.dominancia} I:{self.influencia} S:{self.estabilidade} C:{self.conformidade}"
    
    def calcular_perfil_principal(self):
        """Calcula a letra ou combinação dominante"""
        scores = [
            ('D', self.dominancia),
            ('I', self.influencia),
            ('S', self.estabilidade),
            ('C', self.conformidade),
        ]
        # Ordena por score
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # Se o primeiro é muito maior que o segundo, é perfil puro
        if scores[0][1] - scores[1][1] > 15:
            self.perfil_principal = scores[0][0]
        else:
            # Combinação das duas maiores
            self.perfil_principal = scores[0][0] + scores[1][0]
        
        return self.perfil_principal


# =====================================================
# ENGENHARIA DE CARGOS (PERFIL IDEAL)
# =====================================================

class PerfilIdealCargo(BaseModel):
    """Perfil comportamental ideal para um cargo"""
    cargo = models.OneToOneField('departamento_pessoal.Cargo', on_delete=models.CASCADE, related_name='perfil_ideal')
    
    # Scores DISC ideais (faixas)
    dominancia_min = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    dominancia_ideal = models.IntegerField(default=50, validators=[MinValueValidator(0), MaxValueValidator(100)])
    dominancia_max = models.IntegerField(default=100, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    influencia_min = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    influencia_ideal = models.IntegerField(default=50, validators=[MinValueValidator(0), MaxValueValidator(100)])
    influencia_max = models.IntegerField(default=100, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    estabilidade_min = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    estabilidade_ideal = models.IntegerField(default=50, validators=[MinValueValidator(0), MaxValueValidator(100)])
    estabilidade_max = models.IntegerField(default=100, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    conformidade_min = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    conformidade_ideal = models.IntegerField(default=50, validators=[MinValueValidator(0), MaxValueValidator(100)])
    conformidade_max = models.IntegerField(default=100, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Pesos (importância de cada dimensão para o cargo)
    peso_dominancia = models.IntegerField(default=25, validators=[MinValueValidator(0), MaxValueValidator(100)])
    peso_influencia = models.IntegerField(default=25, validators=[MinValueValidator(0), MaxValueValidator(100)])
    peso_estabilidade = models.IntegerField(default=25, validators=[MinValueValidator(0), MaxValueValidator(100)])
    peso_conformidade = models.IntegerField(default=25, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Competências comportamentais requeridas
    competencias = models.JSONField(default=list, help_text='Lista de competências comportamentais')
    
    # Descrição do perfil ideal
    descricao_perfil = models.TextField(blank=True)
    
    # Responsável pela definição
    definido_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    data_definicao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'gestao_comportamental'
        verbose_name = 'Perfil Ideal do Cargo'
        verbose_name_plural = 'Perfis Ideais dos Cargos'
    
    def __str__(self):
        return f"Perfil Ideal - {self.cargo.nome}"


class CompetenciaComportamental(BaseModel):
    """Competências comportamentais avaliáveis"""
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    
    # Categoria
    categoria = models.CharField(max_length=50, choices=[
        ('lideranca', 'Liderança'),
        ('comunicacao', 'Comunicação'),
        ('relacionamento', 'Relacionamento'),
        ('execucao', 'Execução'),
        ('analise', 'Análise'),
        ('adaptabilidade', 'Adaptabilidade'),
        ('inovacao', 'Inovação'),
        ('organizacao', 'Organização'),
    ])
    
    # Relação com DISC (qual dimensão mais relacionada)
    disc_relacionado = models.CharField(max_length=4, choices=[
        ('D', 'Dominância'),
        ('I', 'Influência'),
        ('S', 'Estabilidade'),
        ('C', 'Conformidade'),
        ('DI', 'Dominância/Influência'),
        ('DC', 'Dominância/Conformidade'),
        ('IS', 'Influência/Estabilidade'),
        ('SC', 'Estabilidade/Conformidade'),
    ], blank=True)
    
    # Indicadores comportamentais
    indicadores_positivos = models.JSONField(default=list)
    indicadores_negativos = models.JSONField(default=list)
    
    class Meta:
        app_label = 'gestao_comportamental'
        verbose_name = 'Competência Comportamental'
        verbose_name_plural = 'Competências Comportamentais'
        ordering = ['categoria', 'nome']
    
    def __str__(self):
        return f"{self.nome} ({self.categoria})"


# =====================================================
# MATCHER (MATCH ENTRE PERFIL E CARGO)
# =====================================================

class MatchComportamental(BaseModel):
    """Match entre um perfil DISC e um cargo"""
    perfil_disc = models.ForeignKey(PerfilDISC, on_delete=models.CASCADE, related_name='matches')
    perfil_ideal = models.ForeignKey(PerfilIdealCargo, on_delete=models.CASCADE, related_name='matches')
    
    # Scores de match por dimensão (0-100%)
    match_dominancia = models.DecimalField(max_digits=5, decimal_places=2)
    match_influencia = models.DecimalField(max_digits=5, decimal_places=2)
    match_estabilidade = models.DecimalField(max_digits=5, decimal_places=2)
    match_conformidade = models.DecimalField(max_digits=5, decimal_places=2)
    
    # Score geral de match (ponderado pelos pesos)
    match_geral = models.DecimalField(max_digits=5, decimal_places=2)
    
    # Classificação do match
    classificacao = models.CharField(max_length=20, choices=[
        ('excelente', 'Excelente (90-100%)'),
        ('muito_bom', 'Muito Bom (75-89%)'),
        ('bom', 'Bom (60-74%)'),
        ('razoavel', 'Razoável (40-59%)'),
        ('baixo', 'Baixo (0-39%)'),
    ])
    
    # Análise detalhada
    pontos_alinhamento = models.JSONField(default=list)
    pontos_atencao = models.JSONField(default=list)
    recomendacoes = models.JSONField(default=list)
    
    # Gerado por IA
    analise_ia = models.TextField(blank=True)
    
    class Meta:
        app_label = 'gestao_comportamental'
        verbose_name = 'Match Comportamental'
        verbose_name_plural = 'Matches Comportamentais'
        unique_together = ['perfil_disc', 'perfil_ideal']
        ordering = ['-match_geral']
    
    def __str__(self):
        return f"Match {self.match_geral}% - {self.perfil_disc.aplicacao} para {self.perfil_ideal.cargo}"
    
    def calcular_match(self):
        """Calcula o match entre o perfil e o cargo"""
        def calc_match_dimensao(valor, min_val, ideal, max_val):
            if min_val <= valor <= max_val:
                # Dentro da faixa aceitável
                if valor == ideal:
                    return 100
                elif valor < ideal:
                    return 100 - ((ideal - valor) / (ideal - min_val) * 30)
                else:
                    return 100 - ((valor - ideal) / (max_val - ideal) * 30)
            else:
                # Fora da faixa
                if valor < min_val:
                    return max(0, 70 - ((min_val - valor) * 2))
                else:
                    return max(0, 70 - ((valor - max_val) * 2))
        
        perfil = self.perfil_disc
        ideal = self.perfil_ideal
        
        self.match_dominancia = calc_match_dimensao(
            perfil.dominancia, ideal.dominancia_min, ideal.dominancia_ideal, ideal.dominancia_max
        )
        self.match_influencia = calc_match_dimensao(
            perfil.influencia, ideal.influencia_min, ideal.influencia_ideal, ideal.influencia_max
        )
        self.match_estabilidade = calc_match_dimensao(
            perfil.estabilidade, ideal.estabilidade_min, ideal.estabilidade_ideal, ideal.estabilidade_max
        )
        self.match_conformidade = calc_match_dimensao(
            perfil.conformidade, ideal.conformidade_min, ideal.conformidade_ideal, ideal.conformidade_max
        )
        
        # Calcula match geral ponderado
        total_peso = ideal.peso_dominancia + ideal.peso_influencia + ideal.peso_estabilidade + ideal.peso_conformidade
        self.match_geral = (
            (self.match_dominancia * ideal.peso_dominancia) +
            (self.match_influencia * ideal.peso_influencia) +
            (self.match_estabilidade * ideal.peso_estabilidade) +
            (self.match_conformidade * ideal.peso_conformidade)
        ) / total_peso
        
        # Classificação
        if self.match_geral >= 90:
            self.classificacao = 'excelente'
        elif self.match_geral >= 75:
            self.classificacao = 'muito_bom'
        elif self.match_geral >= 60:
            self.classificacao = 'bom'
        elif self.match_geral >= 40:
            self.classificacao = 'razoavel'
        else:
            self.classificacao = 'baixo'
        
        return self.match_geral


# =====================================================
# MÉTRICAS DO PROFILER
# =====================================================

class MetricaProfiler(BaseModel):
    """Métricas agregadas do profiler"""
    data_referencia = models.DateField()
    
    # Escopo
    departamento = models.ForeignKey('departamento_pessoal.Departamento', on_delete=models.CASCADE, null=True, blank=True)
    cargo = models.ForeignKey('departamento_pessoal.Cargo', on_delete=models.CASCADE, null=True, blank=True)
    
    # Totais
    total_aplicacoes = models.IntegerField(default=0)
    total_concluidos = models.IntegerField(default=0)
    taxa_conclusao = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Distribuição DISC
    media_dominancia = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    media_influencia = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    media_estabilidade = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    media_conformidade = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Distribuição de perfis principais
    distribuicao_perfis = models.JSONField(default=dict, help_text='Ex: {"D": 10, "I": 15, "S": 8, "C": 12}')
    
    # Match
    media_match = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text='Média de match com perfil ideal')
    
    # Tempo
    tempo_medio_resposta = models.IntegerField(default=0, help_text='Segundos')
    
    class Meta:
        app_label = 'gestao_comportamental'
        verbose_name = 'Métrica Profiler'
        verbose_name_plural = 'Métricas Profiler'
        ordering = ['-data_referencia']
    
    def __str__(self):
        scope = self.departamento or self.cargo or 'Geral'
        return f"Métricas {scope} - {self.data_referencia}"


class ComparacaoTime(BaseModel):
    """Comparação de perfis de um time/departamento"""
    nome = models.CharField(max_length=255)
    descricao = models.TextField(blank=True)
    
    # Escopo
    departamento = models.ForeignKey('departamento_pessoal.Departamento', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Membros comparados
    perfis = models.ManyToManyField(PerfilDISC, related_name='comparacoes')
    
    # Análise
    mapa_time = models.JSONField(default=dict, help_text='Visualização do time no gráfico DISC')
    gaps_identificados = models.JSONField(default=list, help_text='Perfis que faltam no time')
    pontos_fortes_time = models.JSONField(default=list)
    pontos_atencao_time = models.JSONField(default=list)
    
    # Recomendações
    recomendacoes_contratacao = models.TextField(blank=True)
    recomendacoes_desenvolvimento = models.TextField(blank=True)
    
    # IA
    analise_ia = models.TextField(blank=True)
    
    # Criado por
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        app_label = 'gestao_comportamental'
        verbose_name = 'Comparação de Time'
        verbose_name_plural = 'Comparações de Times'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.nome


# =====================================================
# HISTÓRICO E EVOLUÇÃO
# =====================================================

class HistoricoPerfilColaborador(BaseModel):
    """Histórico de perfis de um colaborador ao longo do tempo"""
    colaborador = models.ForeignKey('departamento_pessoal.Colaborador', on_delete=models.CASCADE, related_name='historico_perfis')
    perfil_disc = models.ForeignKey(PerfilDISC, on_delete=models.CASCADE, related_name='historicos')
    
    # Contexto da aplicação
    contexto = models.CharField(max_length=50, choices=[
        ('admissao', 'Admissão'),
        ('promocao', 'Promoção'),
        ('periodico', 'Avaliação Periódica'),
        ('transferencia', 'Transferência'),
        ('desenvolvimento', 'Programa de Desenvolvimento'),
        ('outro', 'Outro'),
    ])
    
    # Comparação com perfil anterior
    perfil_anterior = models.ForeignKey(PerfilDISC, on_delete=models.SET_NULL, null=True, blank=True, related_name='historicos_posteriores')
    variacao_dominancia = models.IntegerField(default=0)
    variacao_influencia = models.IntegerField(default=0)
    variacao_estabilidade = models.IntegerField(default=0)
    variacao_conformidade = models.IntegerField(default=0)
    
    observacoes = models.TextField(blank=True)
    
    class Meta:
        app_label = 'gestao_comportamental'
        verbose_name = 'Histórico de Perfil'
        verbose_name_plural = 'Históricos de Perfis'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.colaborador.nome_completo} - {self.contexto} - {self.created_at.date()}"


# =====================================================
# AGENTE SYNCRH (IA COMPORTAMENTAL)
# =====================================================

class InsightComportamental(BaseModel):
    """Insights gerados pela IA sobre comportamento"""
    tipo = models.CharField(max_length=50, choices=[
        ('compatibilidade', 'Compatibilidade Cargo'),
        ('desenvolvimento', 'Recomendação de Desenvolvimento'),
        ('time', 'Dinâmica de Time'),
        ('lideranca', 'Estilo de Liderança'),
        ('comunicacao', 'Estilo de Comunicação'),
        ('conflito', 'Gestão de Conflitos'),
        ('padrao', 'Padrão Identificado'),
    ])
    
    # Escopo
    colaborador = models.ForeignKey('departamento_pessoal.Colaborador', on_delete=models.CASCADE, null=True, blank=True, related_name='insights_comportamentais')
    departamento = models.ForeignKey('departamento_pessoal.Departamento', on_delete=models.CASCADE, null=True, blank=True, related_name='insights_comportamentais')
    
    # Conteúdo
    titulo = models.CharField(max_length=255)
    descricao = models.TextField()
    dados_suporte = models.JSONField(default=dict, blank=True)
    
    # Prioridade
    prioridade = models.CharField(max_length=20, choices=[
        ('baixa', 'Baixa'),
        ('media', 'Média'),
        ('alta', 'Alta'),
    ], default='media')
    
    # Ação
    acao_sugerida = models.TextField(blank=True)
    acao_tomada = models.BooleanField(default=False)
    
    class Meta:
        app_label = 'gestao_comportamental'
        verbose_name = 'Insight Comportamental'
        verbose_name_plural = 'Insights Comportamentais'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.tipo}: {self.titulo}"
