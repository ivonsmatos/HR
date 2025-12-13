"""
Models do Módulo Desenvolvimento e Performance - SyncRH

Funcionalidades:
- Análise Comparativa (SyncBox/9Box)
- Avaliação de Desempenho (90°, 180°, 360°)
- Plano de Desenvolvimento Individual (PDI)
- People Analytics - Métricas do Colaborador
- Agente SyncRH (IA para feedbacks)
- LMS - Sistema de Gestão de Aprendizagem
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
# ANÁLISE COMPARATIVA (SYNCBOX / 9BOX)
# =====================================================

class CicloAvaliacao(BaseModel):
    """Ciclo de avaliação de desempenho"""
    nome = models.CharField(max_length=255)
    descricao = models.TextField(blank=True)
    ano = models.IntegerField()
    semestre = models.IntegerField(choices=[(1, '1º Semestre'), (2, '2º Semestre')], null=True, blank=True)
    
    data_inicio = models.DateField()
    data_fim = models.DateField()
    
    # Etapas
    data_inicio_autoavaliacao = models.DateField(null=True, blank=True)
    data_fim_autoavaliacao = models.DateField(null=True, blank=True)
    data_inicio_avaliacao_gestor = models.DateField(null=True, blank=True)
    data_fim_avaliacao_gestor = models.DateField(null=True, blank=True)
    data_inicio_calibracao = models.DateField(null=True, blank=True)
    data_fim_calibracao = models.DateField(null=True, blank=True)
    data_feedback = models.DateField(null=True, blank=True)
    
    status = models.CharField(max_length=30, choices=[
        ('planejado', 'Planejado'),
        ('autoavaliacao', 'Autoavaliação'),
        ('avaliacao_gestor', 'Avaliação Gestor'),
        ('calibracao', 'Calibração'),
        ('feedback', 'Feedback'),
        ('concluido', 'Concluído'),
    ], default='planejado')
    
    class Meta:
        app_label = 'desenvolvimento_performance'
        verbose_name = 'Ciclo de Avaliação'
        verbose_name_plural = 'Ciclos de Avaliação'
        ordering = ['-ano', '-semestre']
    
    def __str__(self):
        return f"{self.nome} ({self.ano})"


class SyncBox(BaseModel):
    """Posicionamento do colaborador na matriz 9Box (SyncBox)"""
    colaborador = models.ForeignKey('departamento_pessoal.Colaborador', on_delete=models.CASCADE, related_name='syncbox_historico')
    ciclo = models.ForeignKey(CicloAvaliacao, on_delete=models.CASCADE, related_name='posicionamentos')
    
    # Eixos (1-3)
    desempenho = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(3)], help_text='1=Baixo, 2=Médio, 3=Alto')
    potencial = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(3)], help_text='1=Baixo, 2=Médio, 3=Alto')
    
    # Quadrante calculado (1-9)
    quadrante = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(9)])
    
    # Classificação
    classificacao = models.CharField(max_length=50, choices=[
        ('enigma', 'Enigma'),
        ('forte_potencial', 'Forte Potencial'),
        ('alto_potencial', 'Alto Potencial'),
        ('questionavel', 'Questionável'),
        ('mantenedor', 'Mantenedor'),
        ('forte_desempenho', 'Forte Desempenho'),
        ('insuficiente', 'Insuficiente'),
        ('eficaz', 'Eficaz'),
        ('estrela', 'Estrela'),
    ])
    
    # Recomendações
    recomendacao = models.TextField(blank=True)
    plano_acao = models.TextField(blank=True)
    
    # Avaliador
    avaliado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='syncbox_avaliados')
    
    class Meta:
        app_label = 'desenvolvimento_performance'
        verbose_name = 'SyncBox'
        verbose_name_plural = 'SyncBox'
        unique_together = ['colaborador', 'ciclo']
    
    def __str__(self):
        return f"{self.colaborador.nome_completo} - {self.classificacao}"
    
    def save(self, *args, **kwargs):
        # Calcula o quadrante baseado em desempenho e potencial
        self.quadrante = (self.potencial - 1) * 3 + self.desempenho
        
        # Define a classificação
        classificacoes = {
            1: 'insuficiente', 2: 'eficaz', 3: 'estrela',
            4: 'questionavel', 5: 'mantenedor', 6: 'forte_desempenho',
            7: 'enigma', 8: 'forte_potencial', 9: 'alto_potencial',
        }
        self.classificacao = classificacoes.get(self.quadrante, 'mantenedor')
        
        super().save(*args, **kwargs)


# =====================================================
# AVALIAÇÃO DE DESEMPENHO
# =====================================================

class ModeloAvaliacao(BaseModel):
    """Modelo/template de avaliação"""
    nome = models.CharField(max_length=255)
    descricao = models.TextField(blank=True)
    tipo = models.CharField(max_length=30, choices=[
        ('90', 'Avaliação 90° (Gestor → Colaborador)'),
        ('180', 'Avaliação 180° (Gestor + Autoavaliação)'),
        ('360', 'Avaliação 360° (Múltiplos avaliadores)'),
    ], default='180')
    
    # Configurações
    peso_autoavaliacao = models.IntegerField(default=30, validators=[MinValueValidator(0), MaxValueValidator(100)])
    peso_gestor = models.IntegerField(default=50, validators=[MinValueValidator(0), MaxValueValidator(100)])
    peso_pares = models.IntegerField(default=10, validators=[MinValueValidator(0), MaxValueValidator(100)])
    peso_subordinados = models.IntegerField(default=10, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Escala
    escala_min = models.IntegerField(default=1)
    escala_max = models.IntegerField(default=5)
    
    class Meta:
        app_label = 'desenvolvimento_performance'
        verbose_name = 'Modelo de Avaliação'
        verbose_name_plural = 'Modelos de Avaliação'
    
    def __str__(self):
        return f"{self.nome} ({self.tipo})"


class CriterioAvaliacao(BaseModel):
    """Critérios/competências avaliadas"""
    modelo = models.ForeignKey(ModeloAvaliacao, on_delete=models.CASCADE, related_name='criterios')
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    categoria = models.CharField(max_length=50, choices=[
        ('tecnica', 'Competência Técnica'),
        ('comportamental', 'Competência Comportamental'),
        ('resultado', 'Resultados/Metas'),
        ('lideranca', 'Liderança'),
        ('valores', 'Valores Organizacionais'),
    ])
    peso = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(10)])
    ordem = models.IntegerField(default=0)
    
    class Meta:
        app_label = 'desenvolvimento_performance'
        verbose_name = 'Critério de Avaliação'
        verbose_name_plural = 'Critérios de Avaliação'
        ordering = ['ordem']
    
    def __str__(self):
        return f"{self.modelo.nome} - {self.nome}"


class AvaliacaoDesempenho(BaseModel):
    """Avaliação de desempenho individual"""
    colaborador = models.ForeignKey('departamento_pessoal.Colaborador', on_delete=models.CASCADE, related_name='avaliacoes')
    ciclo = models.ForeignKey(CicloAvaliacao, on_delete=models.CASCADE, related_name='avaliacoes')
    modelo = models.ForeignKey(ModeloAvaliacao, on_delete=models.SET_NULL, null=True)
    
    # Avaliador
    avaliador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='avaliacoes_realizadas')
    tipo_avaliador = models.CharField(max_length=30, choices=[
        ('auto', 'Autoavaliação'),
        ('gestor', 'Gestor'),
        ('par', 'Par/Colega'),
        ('subordinado', 'Subordinado'),
        ('cliente', 'Cliente Interno'),
    ])
    
    # Status
    status = models.CharField(max_length=30, choices=[
        ('pendente', 'Pendente'),
        ('em_andamento', 'Em Andamento'),
        ('concluida', 'Concluída'),
        ('validada', 'Validada'),
    ], default='pendente')
    
    # Notas
    nota_final = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    
    # Feedback
    pontos_fortes = models.TextField(blank=True)
    areas_melhoria = models.TextField(blank=True)
    comentarios = models.TextField(blank=True)
    
    # Datas
    data_inicio = models.DateTimeField(null=True, blank=True)
    data_conclusao = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        app_label = 'desenvolvimento_performance'
        verbose_name = 'Avaliação de Desempenho'
        verbose_name_plural = 'Avaliações de Desempenho'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.colaborador.nome_completo} - {self.ciclo.nome} ({self.tipo_avaliador})"


class RespostaAvaliacao(BaseModel):
    """Respostas individuais da avaliação"""
    avaliacao = models.ForeignKey(AvaliacaoDesempenho, on_delete=models.CASCADE, related_name='respostas')
    criterio = models.ForeignKey(CriterioAvaliacao, on_delete=models.CASCADE)
    nota = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comentario = models.TextField(blank=True)
    
    class Meta:
        app_label = 'desenvolvimento_performance'
        verbose_name = 'Resposta de Avaliação'
        verbose_name_plural = 'Respostas de Avaliação'
        unique_together = ['avaliacao', 'criterio']
    
    def __str__(self):
        return f"{self.avaliacao} - {self.criterio.nome}: {self.nota}"


class ConsolidacaoAvaliacao(BaseModel):
    """Consolidação das avaliações do colaborador"""
    colaborador = models.ForeignKey('departamento_pessoal.Colaborador', on_delete=models.CASCADE, related_name='consolidacoes')
    ciclo = models.ForeignKey(CicloAvaliacao, on_delete=models.CASCADE, related_name='consolidacoes')
    
    # Notas consolidadas
    nota_autoavaliacao = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    nota_gestor = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    nota_pares = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    nota_subordinados = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    nota_final_ponderada = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    
    # Classificação
    classificacao = models.CharField(max_length=50, choices=[
        ('excepcional', 'Excepcional'),
        ('acima_esperado', 'Acima do Esperado'),
        ('atende', 'Atende às Expectativas'),
        ('parcialmente', 'Atende Parcialmente'),
        ('abaixo', 'Abaixo do Esperado'),
    ], blank=True)
    
    # Calibração
    calibrado = models.BooleanField(default=False)
    nota_calibrada = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    justificativa_calibracao = models.TextField(blank=True)
    
    # Feedback final
    feedback_gestor = models.TextField(blank=True)
    feedback_rh = models.TextField(blank=True)
    feedback_entregue = models.BooleanField(default=False)
    data_feedback = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        app_label = 'desenvolvimento_performance'
        verbose_name = 'Consolidação de Avaliação'
        verbose_name_plural = 'Consolidações de Avaliação'
        unique_together = ['colaborador', 'ciclo']
    
    def __str__(self):
        return f"{self.colaborador.nome_completo} - {self.ciclo.nome}"


# =====================================================
# PLANO DE DESENVOLVIMENTO INDIVIDUAL (PDI)
# =====================================================

class PDI(BaseModel):
    """Plano de Desenvolvimento Individual"""
    colaborador = models.ForeignKey('departamento_pessoal.Colaborador', on_delete=models.CASCADE, related_name='pdis')
    ciclo = models.ForeignKey(CicloAvaliacao, on_delete=models.SET_NULL, null=True, blank=True, related_name='pdis')
    
    titulo = models.CharField(max_length=255)
    descricao = models.TextField(blank=True)
    
    # Período
    data_inicio = models.DateField()
    data_fim = models.DateField()
    
    # Status
    status = models.CharField(max_length=30, choices=[
        ('rascunho', 'Rascunho'),
        ('aguardando_aprovacao', 'Aguardando Aprovação'),
        ('aprovado', 'Aprovado'),
        ('em_andamento', 'Em Andamento'),
        ('concluido', 'Concluído'),
        ('cancelado', 'Cancelado'),
    ], default='rascunho')
    
    # Progresso
    progresso = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Aprovações
    aprovado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='pdis_aprovados')
    data_aprovacao = models.DateTimeField(null=True, blank=True)
    
    # Gerado por IA
    gerado_ia = models.BooleanField(default=False)
    
    class Meta:
        app_label = 'desenvolvimento_performance'
        verbose_name = 'PDI'
        verbose_name_plural = 'PDIs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"PDI: {self.colaborador.nome_completo} - {self.titulo}"


class MetaPDI(BaseModel):
    """Metas do PDI"""
    pdi = models.ForeignKey(PDI, on_delete=models.CASCADE, related_name='metas')
    
    titulo = models.CharField(max_length=255)
    descricao = models.TextField(blank=True)
    
    # Categorização
    tipo = models.CharField(max_length=50, choices=[
        ('tecnica', 'Competência Técnica'),
        ('comportamental', 'Competência Comportamental'),
        ('lideranca', 'Liderança'),
        ('carreira', 'Desenvolvimento de Carreira'),
        ('certificacao', 'Certificação'),
        ('projeto', 'Projeto Especial'),
    ])
    
    # Prazo
    data_limite = models.DateField()
    prioridade = models.CharField(max_length=20, choices=[
        ('alta', 'Alta'),
        ('media', 'Média'),
        ('baixa', 'Baixa'),
    ], default='media')
    
    # Status
    status = models.CharField(max_length=30, choices=[
        ('pendente', 'Pendente'),
        ('em_andamento', 'Em Andamento'),
        ('concluida', 'Concluída'),
        ('atrasada', 'Atrasada'),
        ('cancelada', 'Cancelada'),
    ], default='pendente')
    
    progresso = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Vinculação com treinamento
    treinamento = models.ForeignKey('Curso', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Evidências
    evidencias = models.TextField(blank=True)
    
    class Meta:
        app_label = 'desenvolvimento_performance'
        verbose_name = 'Meta do PDI'
        verbose_name_plural = 'Metas do PDI'
        ordering = ['data_limite']
    
    def __str__(self):
        return f"{self.pdi.colaborador.nome_completo} - {self.titulo}"


class AcompanhamentoPDI(BaseModel):
    """Acompanhamentos periódicos do PDI"""
    pdi = models.ForeignKey(PDI, on_delete=models.CASCADE, related_name='acompanhamentos')
    
    data = models.DateField()
    tipo = models.CharField(max_length=30, choices=[
        ('reuniao_1_1', 'Reunião 1:1'),
        ('checkpoint', 'Checkpoint'),
        ('feedback', 'Feedback'),
        ('atualizacao', 'Atualização'),
    ])
    
    descricao = models.TextField()
    proximos_passos = models.TextField(blank=True)
    
    registrado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        app_label = 'desenvolvimento_performance'
        verbose_name = 'Acompanhamento PDI'
        verbose_name_plural = 'Acompanhamentos PDI'
        ordering = ['-data']
    
    def __str__(self):
        return f"{self.pdi.colaborador.nome_completo} - {self.data}"


# =====================================================
# PEOPLE ANALYTICS
# =====================================================

class MetricaColaborador(BaseModel):
    """Métricas individuais do colaborador"""
    colaborador = models.ForeignKey('departamento_pessoal.Colaborador', on_delete=models.CASCADE, related_name='metricas')
    periodo = models.DateField(help_text='Mês de referência')
    
    # Desempenho
    nota_desempenho = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    metas_atingidas = models.IntegerField(default=0)
    metas_total = models.IntegerField(default=0)
    
    # Engajamento
    score_engajamento = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    participacao_pesquisas = models.BooleanField(default=False)
    
    # Desenvolvimento
    treinamentos_concluidos = models.IntegerField(default=0)
    horas_treinamento = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    pdi_progresso = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Comportamental
    feedbacks_recebidos = models.IntegerField(default=0)
    feedbacks_dados = models.IntegerField(default=0)
    reconhecimentos = models.IntegerField(default=0)
    
    # Presença
    dias_trabalhados = models.IntegerField(default=0)
    faltas = models.IntegerField(default=0)
    atrasos = models.IntegerField(default=0)
    
    # Rotatividade (radar)
    risco_rotatividade = models.CharField(max_length=20, choices=[
        ('baixo', 'Baixo'),
        ('medio', 'Médio'),
        ('alto', 'Alto'),
        ('critico', 'Crítico'),
    ], blank=True)
    score_risco = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    class Meta:
        app_label = 'desenvolvimento_performance'
        verbose_name = 'Métrica do Colaborador'
        verbose_name_plural = 'Métricas dos Colaboradores'
        unique_together = ['colaborador', 'periodo']
        ordering = ['-periodo']
    
    def __str__(self):
        return f"{self.colaborador.nome_completo} - {self.periodo}"


class RelatorioAnalytics(BaseModel):
    """Relatórios gerados pelo People Analytics"""
    titulo = models.CharField(max_length=255)
    tipo = models.CharField(max_length=50, choices=[
        ('desempenho', 'Análise de Desempenho'),
        ('engajamento', 'Análise de Engajamento'),
        ('rotatividade', 'Radar de Rotatividade'),
        ('desenvolvimento', 'Desenvolvimento'),
        ('clima', 'Clima Organizacional'),
        ('comparativo', 'Análise Comparativa'),
        ('tendencias', 'Tendências'),
        ('customizado', 'Customizado'),
    ])
    
    # Período
    periodo_inicio = models.DateField()
    periodo_fim = models.DateField()
    
    # Escopo
    departamento = models.ForeignKey('departamento_pessoal.Departamento', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Conteúdo
    dados = models.JSONField(default=dict)
    insights = models.JSONField(default=list, help_text='Insights gerados pela IA')
    recomendacoes = models.JSONField(default=list)
    
    # Arquivo
    arquivo_pdf = models.FileField(upload_to='analytics/relatorios/', null=True, blank=True)
    
    # Geração
    gerado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        app_label = 'desenvolvimento_performance'
        verbose_name = 'Relatório Analytics'
        verbose_name_plural = 'Relatórios Analytics'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.titulo} ({self.tipo})"


# =====================================================
# LMS - SISTEMA DE GESTÃO DE APRENDIZAGEM
# =====================================================

class CategoriaCurso(BaseModel):
    """Categorias de cursos"""
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    cor = models.CharField(max_length=7, default='#3498db')
    icone = models.CharField(max_length=50, default='book')
    
    class Meta:
        app_label = 'desenvolvimento_performance'
        verbose_name = 'Categoria de Curso'
        verbose_name_plural = 'Categorias de Cursos'
    
    def __str__(self):
        return self.nome


class Curso(BaseModel):
    """Cursos do LMS"""
    titulo = models.CharField(max_length=255)
    codigo = models.CharField(max_length=50, unique=True)
    descricao = models.TextField()
    categoria = models.ForeignKey(CategoriaCurso, on_delete=models.SET_NULL, null=True, related_name='cursos')
    
    # Mídia
    imagem_capa = models.ImageField(upload_to='lms/cursos/', null=True, blank=True)
    video_intro = models.URLField(blank=True)
    
    # Detalhes
    carga_horaria = models.DecimalField(max_digits=5, decimal_places=2, help_text='Horas')
    nivel = models.CharField(max_length=30, choices=[
        ('iniciante', 'Iniciante'),
        ('intermediario', 'Intermediário'),
        ('avancado', 'Avançado'),
    ], default='iniciante')
    
    # Instrutores
    instrutor = models.CharField(max_length=255, blank=True)
    
    # Requisitos
    pre_requisitos = models.TextField(blank=True)
    publico_alvo = models.TextField(blank=True)
    
    # Certificação
    emite_certificado = models.BooleanField(default=True)
    nota_minima_aprovacao = models.IntegerField(default=70, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Status
    status = models.CharField(max_length=30, choices=[
        ('rascunho', 'Rascunho'),
        ('publicado', 'Publicado'),
        ('arquivado', 'Arquivado'),
    ], default='rascunho')
    
    # Obrigatoriedade
    obrigatorio = models.BooleanField(default=False)
    departamentos_obrigatorios = models.ManyToManyField('departamento_pessoal.Departamento', blank=True, related_name='cursos_obrigatorios')
    cargos_obrigatorios = models.ManyToManyField('departamento_pessoal.Cargo', blank=True, related_name='cursos_obrigatorios')
    
    # Estatísticas
    total_matriculas = models.IntegerField(default=0)
    total_conclusoes = models.IntegerField(default=0)
    avaliacao_media = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    
    class Meta:
        app_label = 'desenvolvimento_performance'
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.titulo


class ModuloCurso(BaseModel):
    """Módulos do curso"""
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='modulos')
    titulo = models.CharField(max_length=255)
    descricao = models.TextField(blank=True)
    ordem = models.IntegerField(default=0)
    
    class Meta:
        app_label = 'desenvolvimento_performance'
        verbose_name = 'Módulo do Curso'
        verbose_name_plural = 'Módulos do Curso'
        ordering = ['ordem']
    
    def __str__(self):
        return f"{self.curso.titulo} - {self.titulo}"


class AulaCurso(BaseModel):
    """Aulas/conteúdos do módulo"""
    modulo = models.ForeignKey(ModuloCurso, on_delete=models.CASCADE, related_name='aulas')
    titulo = models.CharField(max_length=255)
    descricao = models.TextField(blank=True)
    ordem = models.IntegerField(default=0)
    
    # Tipo de conteúdo
    tipo = models.CharField(max_length=30, choices=[
        ('video', 'Vídeo'),
        ('texto', 'Texto/Artigo'),
        ('pdf', 'PDF'),
        ('quiz', 'Quiz'),
        ('atividade', 'Atividade Prática'),
        ('link', 'Link Externo'),
    ])
    
    # Conteúdo
    conteudo_texto = models.TextField(blank=True)
    url_video = models.URLField(blank=True)
    arquivo = models.FileField(upload_to='lms/aulas/', null=True, blank=True)
    url_externa = models.URLField(blank=True)
    
    # Duração
    duracao_minutos = models.IntegerField(default=0)
    
    # Quiz
    perguntas_quiz = models.JSONField(default=list, blank=True)
    
    class Meta:
        app_label = 'desenvolvimento_performance'
        verbose_name = 'Aula do Curso'
        verbose_name_plural = 'Aulas do Curso'
        ordering = ['ordem']
    
    def __str__(self):
        return f"{self.modulo.titulo} - {self.titulo}"


class MatriculaCurso(BaseModel):
    """Matrículas de colaboradores em cursos"""
    colaborador = models.ForeignKey('departamento_pessoal.Colaborador', on_delete=models.CASCADE, related_name='matriculas_curso')
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='matriculas')
    
    # Status
    status = models.CharField(max_length=30, choices=[
        ('matriculado', 'Matriculado'),
        ('em_andamento', 'Em Andamento'),
        ('concluido', 'Concluído'),
        ('reprovado', 'Reprovado'),
        ('cancelado', 'Cancelado'),
        ('expirado', 'Expirado'),
    ], default='matriculado')
    
    # Progresso
    progresso = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    aulas_concluidas = models.IntegerField(default=0)
    
    # Notas
    nota_final = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    aprovado = models.BooleanField(default=False)
    
    # Datas
    data_matricula = models.DateTimeField(auto_now_add=True)
    data_inicio = models.DateTimeField(null=True, blank=True)
    data_conclusao = models.DateTimeField(null=True, blank=True)
    data_limite = models.DateField(null=True, blank=True)
    
    # Certificado
    certificado_emitido = models.BooleanField(default=False)
    certificado_url = models.URLField(blank=True)
    
    # Avaliação do curso
    avaliacao_curso = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    comentario_curso = models.TextField(blank=True)
    
    class Meta:
        app_label = 'desenvolvimento_performance'
        verbose_name = 'Matrícula'
        verbose_name_plural = 'Matrículas'
        unique_together = ['colaborador', 'curso']
    
    def __str__(self):
        return f"{self.colaborador.nome_completo} - {self.curso.titulo}"


class ProgressoAula(BaseModel):
    """Progresso do colaborador em cada aula"""
    matricula = models.ForeignKey(MatriculaCurso, on_delete=models.CASCADE, related_name='progressos')
    aula = models.ForeignKey(AulaCurso, on_delete=models.CASCADE)
    
    concluida = models.BooleanField(default=False)
    data_inicio = models.DateTimeField(null=True, blank=True)
    data_conclusao = models.DateTimeField(null=True, blank=True)
    tempo_gasto_minutos = models.IntegerField(default=0)
    
    # Quiz
    nota_quiz = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    respostas_quiz = models.JSONField(default=dict, blank=True)
    tentativas_quiz = models.IntegerField(default=0)
    
    class Meta:
        app_label = 'desenvolvimento_performance'
        verbose_name = 'Progresso da Aula'
        verbose_name_plural = 'Progressos das Aulas'
        unique_together = ['matricula', 'aula']
    
    def __str__(self):
        return f"{self.matricula.colaborador.nome_completo} - {self.aula.titulo}"


# =====================================================
# AGENTE SYNCRH (IA PARA DESENVOLVIMENTO)
# =====================================================

class FeedbackIA(BaseModel):
    """Feedbacks e PDIs gerados por IA"""
    tipo = models.CharField(max_length=50, choices=[
        ('feedback_avaliacao', 'Feedback de Avaliação'),
        ('pdi_sugerido', 'PDI Sugerido'),
        ('analise_desempenho', 'Análise de Desempenho'),
        ('recomendacao_treinamento', 'Recomendação de Treinamento'),
        ('insights_equipe', 'Insights da Equipe'),
    ])
    
    # Referências
    colaborador = models.ForeignKey('departamento_pessoal.Colaborador', on_delete=models.CASCADE, null=True, blank=True, related_name='feedbacks_ia')
    avaliacao = models.ForeignKey(AvaliacaoDesempenho, on_delete=models.CASCADE, null=True, blank=True, related_name='feedbacks_ia')
    pdi = models.ForeignKey(PDI, on_delete=models.CASCADE, null=True, blank=True, related_name='feedbacks_ia')
    
    # Conteúdo
    conteudo = models.TextField()
    contexto = models.JSONField(default=dict, blank=True)
    
    # Feedback do usuário
    utilizado = models.BooleanField(default=False)
    avaliacao_usuario = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    solicitado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        app_label = 'desenvolvimento_performance'
        verbose_name = 'Feedback IA'
        verbose_name_plural = 'Feedbacks IA'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.tipo} - {self.created_at}"
