"""
Models do Módulo Recrutamento e Seleção - SyncRH

Funcionalidades:
- Engenharia de Cargos
- Profiler (Mapeamento Comportamental)
- Matcher (Inteligência Comportamental)
- Banco Unificado de Talentos
- Métricas de Recrutamento
- Página de Carreiras
- Agente SyncRH (IA)
"""

from django.db import models
from django.contrib.auth.models import User
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
# ENGENHARIA DE CARGOS
# =====================================================

class PerfilCargo(BaseModel):
    """Perfil comportamental ideal para cada cargo"""
    nome = models.CharField(max_length=255)
    codigo = models.CharField(max_length=50, unique=True)
    descricao = models.TextField(blank=True)
    
    # Perfil DISC
    dominancia = models.IntegerField(default=50, validators=[MinValueValidator(0), MaxValueValidator(100)])
    influencia = models.IntegerField(default=50, validators=[MinValueValidator(0), MaxValueValidator(100)])
    estabilidade = models.IntegerField(default=50, validators=[MinValueValidator(0), MaxValueValidator(100)])
    conformidade = models.IntegerField(default=50, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Competências requeridas
    competencias_tecnicas = models.JSONField(default=list, help_text='Lista de competências técnicas')
    competencias_comportamentais = models.JSONField(default=list, help_text='Lista de competências comportamentais')
    
    # Requisitos
    escolaridade_minima = models.CharField(max_length=100, blank=True)
    experiencia_minima = models.IntegerField(default=0, help_text='Anos de experiência mínima')
    idiomas = models.JSONField(default=list, help_text='Lista de idiomas requeridos')
    
    # Template
    is_template = models.BooleanField(default=False, help_text='Marcar como template reutilizável')
    
    class Meta:
        verbose_name = 'Perfil de Cargo'
        verbose_name_plural = 'Perfis de Cargos'
        ordering = ['nome']
    
    def __str__(self):
        return self.nome


class CompetenciaCargo(BaseModel):
    """Competências associadas a um cargo"""
    perfil_cargo = models.ForeignKey(PerfilCargo, on_delete=models.CASCADE, related_name='competencias')
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=30, choices=[
        ('tecnica', 'Técnica'),
        ('comportamental', 'Comportamental'),
        ('lideranca', 'Liderança'),
        ('comunicacao', 'Comunicação'),
    ])
    peso = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(5)])
    nivel_minimo = models.IntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(5)])
    descricao = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Competência do Cargo'
        verbose_name_plural = 'Competências do Cargo'
    
    def __str__(self):
        return f"{self.perfil_cargo.nome} - {self.nome}"


# =====================================================
# PROFILER (MAPEAMENTO COMPORTAMENTAL)
# =====================================================

class PerfilComportamental(BaseModel):
    """Perfil comportamental de candidatos e colaboradores"""
    # Pessoa associada
    candidato = models.ForeignKey('Candidato', on_delete=models.CASCADE, null=True, blank=True, related_name='perfis_comportamentais')
    colaborador = models.ForeignKey('departamento_pessoal.Colaborador', on_delete=models.CASCADE, null=True, blank=True, related_name='perfis_comportamentais')
    
    # Data do mapeamento
    data_mapeamento = models.DateTimeField(auto_now_add=True)
    
    # Perfil DISC
    dominancia = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    influencia = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    estabilidade = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    conformidade = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Perfil dominante
    perfil_dominante = models.CharField(max_length=50, choices=[
        ('dominante', 'Dominante (D)'),
        ('influente', 'Influente (I)'),
        ('estavel', 'Estável (S)'),
        ('conforme', 'Conforme (C)'),
        ('di', 'Dominante-Influente (DI)'),
        ('id', 'Influente-Dominante (ID)'),
        ('is', 'Influente-Estável (IS)'),
        ('si', 'Estável-Influente (SI)'),
        ('sc', 'Estável-Conforme (SC)'),
        ('cs', 'Conforme-Estável (CS)'),
        ('cd', 'Conforme-Dominante (CD)'),
        ('dc', 'Dominante-Conforme (DC)'),
    ], blank=True)
    
    # +50 informações comportamentais
    informacoes_detalhadas = models.JSONField(default=dict, help_text='Dados detalhados do mapeamento')
    
    # Pontos fortes e áreas de desenvolvimento
    pontos_fortes = models.JSONField(default=list)
    areas_desenvolvimento = models.JSONField(default=list)
    
    # Estilo de trabalho
    estilo_comunicacao = models.TextField(blank=True)
    estilo_lideranca = models.TextField(blank=True)
    ambiente_ideal = models.TextField(blank=True)
    fatores_motivacionais = models.JSONField(default=list)
    fatores_estresse = models.JSONField(default=list)
    
    # Compatibilidade
    compatibilidade_equipe = models.JSONField(default=dict, blank=True)
    
    # Link de preenchimento
    token_preenchimento = models.CharField(max_length=100, unique=True, blank=True)
    preenchido = models.BooleanField(default=False)
    data_preenchimento = models.DateTimeField(null=True, blank=True)
    
    # Respostas do questionário
    respostas = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name = 'Perfil Comportamental'
        verbose_name_plural = 'Perfis Comportamentais'
        ordering = ['-data_mapeamento']
    
    def __str__(self):
        pessoa = self.candidato or self.colaborador
        return f"Perfil de {pessoa}" if pessoa else f"Perfil #{self.id}"
    
    def calcular_perfil_dominante(self):
        """Calcula o perfil dominante baseado nos scores DISC"""
        scores = {
            'D': self.dominancia,
            'I': self.influencia,
            'S': self.estabilidade,
            'C': self.conformidade,
        }
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        primeiro, segundo = sorted_scores[0], sorted_scores[1]
        
        if primeiro[1] - segundo[1] > 15:
            perfis_map = {'D': 'dominante', 'I': 'influente', 'S': 'estavel', 'C': 'conforme'}
            self.perfil_dominante = perfis_map[primeiro[0]]
        else:
            self.perfil_dominante = f"{primeiro[0].lower()}{segundo[0].lower()}"
        self.save()


# =====================================================
# MATCHER (INTELIGÊNCIA COMPORTAMENTAL)
# =====================================================

class MatchPerfil(BaseModel):
    """Match entre perfil comportamental e cargo"""
    perfil_comportamental = models.ForeignKey(PerfilComportamental, on_delete=models.CASCADE, related_name='matches')
    perfil_cargo = models.ForeignKey(PerfilCargo, on_delete=models.CASCADE, related_name='matches')
    vaga = models.ForeignKey('Vaga', on_delete=models.CASCADE, null=True, blank=True, related_name='matches')
    
    # Scores de aderência
    aderencia_geral = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text='Porcentagem de aderência')
    aderencia_disc = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    aderencia_competencias = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Detalhamento
    competencias_atendidas = models.JSONField(default=list)
    competencias_desenvolver = models.JSONField(default=list)
    gaps_identificados = models.JSONField(default=list)
    
    # Recomendações da IA
    recomendacao = models.CharField(max_length=30, choices=[
        ('altamente_recomendado', 'Altamente Recomendado'),
        ('recomendado', 'Recomendado'),
        ('potencial', 'Potencial'),
        ('nao_recomendado', 'Não Recomendado'),
    ], blank=True)
    
    justificativa_ia = models.TextField(blank=True, help_text='Justificativa gerada pela IA')
    
    class Meta:
        verbose_name = 'Match de Perfil'
        verbose_name_plural = 'Matches de Perfil'
        unique_together = ['perfil_comportamental', 'perfil_cargo', 'vaga']
    
    def __str__(self):
        return f"Match: {self.perfil_comportamental} ↔ {self.perfil_cargo.nome} ({self.aderencia_geral}%)"


# =====================================================
# BANCO UNIFICADO DE TALENTOS
# =====================================================

class Candidato(BaseModel):
    """Candidatos no banco de talentos"""
    # Dados pessoais
    nome = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20, blank=True)
    cpf = models.CharField(max_length=14, blank=True)
    data_nascimento = models.DateField(null=True, blank=True)
    
    # Localização
    cidade = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=2, blank=True)
    pais = models.CharField(max_length=50, default='Brasil')
    
    # Currículo
    curriculo = models.FileField(upload_to='candidatos/curriculos/', null=True, blank=True)
    curriculo_texto = models.TextField(blank=True, help_text='Texto extraído do currículo para busca')
    foto = models.ImageField(upload_to='candidatos/fotos/', null=True, blank=True)
    linkedin = models.URLField(blank=True)
    portfolio = models.URLField(blank=True)
    
    # Formação
    escolaridade = models.CharField(max_length=100, choices=[
        ('fundamental_incompleto', 'Fundamental Incompleto'),
        ('fundamental_completo', 'Fundamental Completo'),
        ('medio_incompleto', 'Médio Incompleto'),
        ('medio_completo', 'Médio Completo'),
        ('tecnico', 'Técnico'),
        ('superior_incompleto', 'Superior Incompleto'),
        ('superior_completo', 'Superior Completo'),
        ('pos_graduacao', 'Pós-Graduação'),
        ('mestrado', 'Mestrado'),
        ('doutorado', 'Doutorado'),
    ], blank=True)
    area_formacao = models.CharField(max_length=100, blank=True)
    instituicao = models.CharField(max_length=255, blank=True)
    
    # Experiência
    anos_experiencia = models.IntegerField(default=0)
    area_atuacao = models.CharField(max_length=100, blank=True)
    cargo_atual = models.CharField(max_length=100, blank=True)
    empresa_atual = models.CharField(max_length=255, blank=True)
    
    # Skills e palavras-chave
    habilidades = models.JSONField(default=list, help_text='Lista de habilidades')
    idiomas = models.JSONField(default=list, help_text='Lista de idiomas')
    certificacoes = models.JSONField(default=list, help_text='Lista de certificações')
    palavras_chave = models.JSONField(default=list, help_text='Palavras-chave para busca')
    
    # Preferências
    pretensao_salarial = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    disponibilidade = models.CharField(max_length=50, choices=[
        ('imediata', 'Imediata'),
        ('15_dias', '15 Dias'),
        ('30_dias', '30 Dias'),
        ('60_dias', '60 Dias'),
        ('negociar', 'A Negociar'),
    ], blank=True)
    aceita_remoto = models.BooleanField(default=True)
    aceita_hibrido = models.BooleanField(default=True)
    aceita_presencial = models.BooleanField(default=True)
    
    # Origem
    origem = models.CharField(max_length=50, choices=[
        ('site_carreiras', 'Site de Carreiras'),
        ('linkedin', 'LinkedIn'),
        ('indicacao', 'Indicação'),
        ('hunters', 'Hunters'),
        ('feira', 'Feira de Emprego'),
        ('banco_externo', 'Banco Externo'),
        ('outros', 'Outros'),
    ], blank=True)
    
    # Tags e classificação
    tags = models.JSONField(default=list)
    estrelas = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    favorito = models.BooleanField(default=False)
    
    # Blacklist
    blacklist = models.BooleanField(default=False)
    motivo_blacklist = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Candidato'
        verbose_name_plural = 'Candidatos'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.nome


class ExperienciaProfissional(BaseModel):
    """Experiências profissionais do candidato"""
    candidato = models.ForeignKey(Candidato, on_delete=models.CASCADE, related_name='experiencias')
    empresa = models.CharField(max_length=255)
    cargo = models.CharField(max_length=100)
    data_inicio = models.DateField()
    data_fim = models.DateField(null=True, blank=True)
    atual = models.BooleanField(default=False)
    descricao = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Experiência Profissional'
        verbose_name_plural = 'Experiências Profissionais'
        ordering = ['-data_inicio']
    
    def __str__(self):
        return f"{self.candidato.nome} - {self.cargo} @ {self.empresa}"


# =====================================================
# VAGAS E PROCESSO SELETIVO
# =====================================================

class Vaga(BaseModel):
    """Vagas abertas"""
    titulo = models.CharField(max_length=255)
    codigo = models.CharField(max_length=50, unique=True)
    perfil_cargo = models.ForeignKey(PerfilCargo, on_delete=models.SET_NULL, null=True, related_name='vagas')
    
    # Descrição
    descricao = models.TextField()
    responsabilidades = models.TextField(blank=True)
    requisitos = models.TextField(blank=True)
    beneficios = models.TextField(blank=True)
    
    # Detalhes
    tipo_contrato = models.CharField(max_length=30, choices=[
        ('clt', 'CLT'),
        ('pj', 'PJ'),
        ('estagio', 'Estágio'),
        ('temporario', 'Temporário'),
        ('trainee', 'Trainee'),
        ('freelancer', 'Freelancer'),
    ], default='clt')
    
    modalidade = models.CharField(max_length=30, choices=[
        ('presencial', 'Presencial'),
        ('remoto', 'Remoto'),
        ('hibrido', 'Híbrido'),
    ], default='presencial')
    
    cidade = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=2, blank=True)
    
    # Salário
    faixa_salarial_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    faixa_salarial_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    exibir_salario = models.BooleanField(default=False)
    
    # Quantidade
    quantidade_vagas = models.IntegerField(default=1)
    
    # Datas
    data_abertura = models.DateField(auto_now_add=True)
    data_limite = models.DateField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=30, choices=[
        ('rascunho', 'Rascunho'),
        ('aberta', 'Aberta'),
        ('em_processo', 'Em Processo Seletivo'),
        ('pausada', 'Pausada'),
        ('fechada', 'Fechada'),
        ('cancelada', 'Cancelada'),
    ], default='rascunho')
    
    # Responsável
    recrutador = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='vagas_responsavel')
    gestor_vaga = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='vagas_gestor')
    
    # Publicação
    publicar_site_carreiras = models.BooleanField(default=True)
    publicar_linkedin = models.BooleanField(default=False)
    
    # Etapas do processo
    etapas = models.JSONField(default=list, help_text='Etapas do processo seletivo')
    
    class Meta:
        verbose_name = 'Vaga'
        verbose_name_plural = 'Vagas'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.titulo} ({self.codigo})"


class CandidaturaVaga(BaseModel):
    """Candidaturas para vagas"""
    candidato = models.ForeignKey(Candidato, on_delete=models.CASCADE, related_name='candidaturas')
    vaga = models.ForeignKey(Vaga, on_delete=models.CASCADE, related_name='candidaturas')
    
    # Status
    etapa_atual = models.CharField(max_length=50, default='triagem')
    status = models.CharField(max_length=30, choices=[
        ('inscrito', 'Inscrito'),
        ('em_triagem', 'Em Triagem'),
        ('aprovado_triagem', 'Aprovado na Triagem'),
        ('reprovado_triagem', 'Reprovado na Triagem'),
        ('entrevista_agendada', 'Entrevista Agendada'),
        ('entrevista_realizada', 'Entrevista Realizada'),
        ('teste_pendente', 'Teste Pendente'),
        ('teste_realizado', 'Teste Realizado'),
        ('aprovado', 'Aprovado'),
        ('reprovado', 'Reprovado'),
        ('desistiu', 'Desistiu'),
        ('contratado', 'Contratado'),
    ], default='inscrito')
    
    # Match
    match_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    match_detalhes = models.JSONField(default=dict, blank=True)
    
    # Avaliações
    nota_triagem = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(10)])
    nota_entrevista = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(10)])
    nota_teste = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(10)])
    nota_final = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    
    # Histórico
    historico_etapas = models.JSONField(default=list)
    
    # Feedback
    feedback_recrutador = models.TextField(blank=True)
    feedback_gestor = models.TextField(blank=True)
    motivo_reprovacao = models.TextField(blank=True)
    
    # Responsável
    recrutador_responsavel = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='candidaturas_responsavel')
    
    class Meta:
        verbose_name = 'Candidatura'
        verbose_name_plural = 'Candidaturas'
        unique_together = ['candidato', 'vaga']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.candidato.nome} → {self.vaga.titulo}"


class Entrevista(BaseModel):
    """Entrevistas agendadas"""
    candidatura = models.ForeignKey(CandidaturaVaga, on_delete=models.CASCADE, related_name='entrevistas')
    
    tipo = models.CharField(max_length=30, choices=[
        ('triagem', 'Triagem'),
        ('tecnica', 'Técnica'),
        ('comportamental', 'Comportamental'),
        ('gestor', 'Com Gestor'),
        ('final', 'Final'),
    ])
    
    # Agendamento
    data_hora = models.DateTimeField()
    duracao_minutos = models.IntegerField(default=60)
    local = models.CharField(max_length=255, blank=True)
    link_videoconferencia = models.URLField(blank=True)
    
    # Participantes
    entrevistadores = models.ManyToManyField(User, related_name='entrevistas_participante')
    
    # Status
    status = models.CharField(max_length=30, choices=[
        ('agendada', 'Agendada'),
        ('confirmada', 'Confirmada'),
        ('realizada', 'Realizada'),
        ('cancelada', 'Cancelada'),
        ('remarcada', 'Remarcada'),
        ('no_show', 'No Show'),
    ], default='agendada')
    
    # Avaliação
    roteiro = models.TextField(blank=True, help_text='Roteiro/perguntas da entrevista')
    anotacoes = models.TextField(blank=True)
    nota = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(10)])
    parecer = models.CharField(max_length=30, choices=[
        ('aprovado', 'Aprovado'),
        ('reprovado', 'Reprovado'),
        ('pendente', 'Pendente Avaliação'),
    ], blank=True)
    
    # Roteiro gerado por IA
    roteiro_ia = models.TextField(blank=True, help_text='Roteiro sugerido pelo Agente SyncRH')
    
    class Meta:
        verbose_name = 'Entrevista'
        verbose_name_plural = 'Entrevistas'
        ordering = ['data_hora']
    
    def __str__(self):
        return f"{self.candidatura.candidato.nome} - {self.tipo} em {self.data_hora}"


# =====================================================
# MÉTRICAS DE RECRUTAMENTO
# =====================================================

class MetricaRecrutamento(BaseModel):
    """Métricas e KPIs de recrutamento"""
    vaga = models.ForeignKey(Vaga, on_delete=models.CASCADE, null=True, blank=True, related_name='metricas')
    periodo_inicio = models.DateField()
    periodo_fim = models.DateField()
    
    # Métricas de funil
    total_candidatos = models.IntegerField(default=0)
    candidatos_triados = models.IntegerField(default=0)
    candidatos_entrevistados = models.IntegerField(default=0)
    candidatos_aprovados = models.IntegerField(default=0)
    candidatos_contratados = models.IntegerField(default=0)
    
    # Taxas
    taxa_conversao_triagem = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    taxa_conversao_entrevista = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    taxa_conversao_final = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Tempo
    tempo_medio_preenchimento = models.IntegerField(default=0, help_text='Dias médios para preencher vaga')
    tempo_medio_triagem = models.IntegerField(default=0, help_text='Dias médios na triagem')
    tempo_medio_processo = models.IntegerField(default=0, help_text='Dias médios no processo todo')
    
    # Custo
    custo_por_contratacao = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Qualidade
    qualidade_contratacoes = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    retencao_90_dias = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Origem
    candidatos_por_origem = models.JSONField(default=dict)
    
    class Meta:
        verbose_name = 'Métrica de Recrutamento'
        verbose_name_plural = 'Métricas de Recrutamento'
        ordering = ['-periodo_fim']
    
    def __str__(self):
        return f"Métricas {self.periodo_inicio} a {self.periodo_fim}"


# =====================================================
# PÁGINA DE CARREIRAS
# =====================================================

class PaginaCarreiras(BaseModel):
    """Configuração da página de carreiras"""
    # Conteúdo
    titulo = models.CharField(max_length=255, default='Carreiras')
    subtitulo = models.CharField(max_length=500, blank=True)
    descricao = models.TextField(blank=True)
    
    # Sobre a empresa
    sobre_empresa = models.TextField(blank=True)
    missao = models.TextField(blank=True)
    visao = models.TextField(blank=True)
    valores = models.JSONField(default=list)
    
    # Mídia
    logo = models.ImageField(upload_to='carreiras/', null=True, blank=True)
    banner = models.ImageField(upload_to='carreiras/', null=True, blank=True)
    video_institucional = models.URLField(blank=True)
    
    # Redes sociais
    linkedin_empresa = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    glassdoor = models.URLField(blank=True)
    
    # SEO
    meta_description = models.CharField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)
    
    # Personalização
    cor_primaria = models.CharField(max_length=7, default='#3498db')
    cor_secundaria = models.CharField(max_length=7, default='#2ecc71')
    
    class Meta:
        verbose_name = 'Página de Carreiras'
        verbose_name_plural = 'Páginas de Carreiras'
    
    def __str__(self):
        return self.titulo


class DepoimentoColaborador(BaseModel):
    """Depoimentos de colaboradores para página de carreiras"""
    pagina = models.ForeignKey(PaginaCarreiras, on_delete=models.CASCADE, related_name='depoimentos')
    nome = models.CharField(max_length=255)
    cargo = models.CharField(max_length=100)
    departamento = models.CharField(max_length=100, blank=True)
    foto = models.ImageField(upload_to='carreiras/depoimentos/', null=True, blank=True)
    depoimento = models.TextField()
    destaque = models.BooleanField(default=False)
    ordem = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = 'Depoimento de Colaborador'
        verbose_name_plural = 'Depoimentos de Colaboradores'
        ordering = ['ordem']
    
    def __str__(self):
        return f"{self.nome} - {self.cargo}"


# =====================================================
# AGENTE SYNCRH (IA)
# =====================================================

class SugestaoIA(BaseModel):
    """Sugestões e outputs do Agente SyncRH para R&S"""
    tipo = models.CharField(max_length=50, choices=[
        ('roteiro_entrevista', 'Roteiro de Entrevista'),
        ('feedback_candidato', 'Feedback para Candidato'),
        ('analise_curriculo', 'Análise de Currículo'),
        ('match_vaga', 'Match com Vaga'),
        ('descricao_vaga', 'Descrição de Vaga'),
        ('email_candidato', 'E-mail para Candidato'),
        ('triagem_automatica', 'Triagem Automática'),
        ('recomendacao', 'Recomendação'),
    ])
    
    # Referências
    vaga = models.ForeignKey(Vaga, on_delete=models.CASCADE, null=True, blank=True, related_name='sugestoes_ia')
    candidato = models.ForeignKey(Candidato, on_delete=models.CASCADE, null=True, blank=True, related_name='sugestoes_ia')
    candidatura = models.ForeignKey(CandidaturaVaga, on_delete=models.CASCADE, null=True, blank=True, related_name='sugestoes_ia')
    
    # Conteúdo
    prompt_usado = models.TextField(blank=True)
    conteudo = models.TextField()
    contexto = models.JSONField(default=dict, blank=True)
    
    # Feedback
    utilizado = models.BooleanField(default=False)
    avaliacao = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    feedback_usuario = models.TextField(blank=True)
    
    # Usuário
    solicitado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name = 'Sugestão IA'
        verbose_name_plural = 'Sugestões IA'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.tipo} - {self.created_at}"
