"""
Models do Módulo Departamento Pessoal - SyncRH

Funcionalidades:
- Controle de Ponto Digital
- Folha de Pagamento Digital
- Admissão Digital
- Gestão Eletrônica de Documentos (GED)
- Gestão de Férias
- Integração Contábil
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
# CONTROLE DE PONTO DIGITAL
# =====================================================

class Colaborador(BaseModel):
    """Cadastro de colaboradores"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='colaborador_dp'
    )
    nome_completo = models.CharField(max_length=255)
    cpf = models.CharField(max_length=14, unique=True)
    data_nascimento = models.DateField(null=True, blank=True)
    data_admissao = models.DateField()
    data_demissao = models.DateField(null=True, blank=True)
    cargo = models.ForeignKey('Cargo', on_delete=models.SET_NULL, null=True, related_name='colaboradores')
    departamento = models.ForeignKey('Departamento', on_delete=models.SET_NULL, null=True, related_name='colaboradores')
    gestor = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinados')
    
    # Dados de contato
    email_pessoal = models.EmailField(blank=True)
    telefone = models.CharField(max_length=20, blank=True)
    endereco = models.TextField(blank=True)
    
    # Dados bancários
    banco = models.CharField(max_length=100, blank=True)
    agencia = models.CharField(max_length=20, blank=True)
    conta = models.CharField(max_length=30, blank=True)
    tipo_conta = models.CharField(max_length=20, choices=[
        ('corrente', 'Conta Corrente'),
        ('poupanca', 'Conta Poupança'),
        ('salario', 'Conta Salário'),
    ], default='corrente')
    
    # Reconhecimento facial
    foto_perfil = models.ImageField(upload_to='colaboradores/fotos/', null=True, blank=True)
    face_encoding = models.JSONField(null=True, blank=True, help_text='Encoding facial para reconhecimento')
    
    class Meta:
        app_label = 'departamento_pessoal'
        verbose_name = 'Colaborador'
        verbose_name_plural = 'Colaboradores'
        ordering = ['nome_completo']
    
    def __str__(self):
        return self.nome_completo


class Departamento(BaseModel):
    """Departamentos da empresa"""
    nome = models.CharField(max_length=100)
    codigo = models.CharField(max_length=20, unique=True)
    descricao = models.TextField(blank=True)
    responsavel = models.ForeignKey(Colaborador, on_delete=models.SET_NULL, null=True, blank=True, related_name='departamentos_responsavel')
    
    class Meta:
        verbose_name = 'Departamento'
        verbose_name_plural = 'Departamentos'
        ordering = ['nome']
    
    def __str__(self):
        return self.nome


class Cargo(BaseModel):
    """Cargos da empresa"""
    nome = models.CharField(max_length=100)
    codigo = models.CharField(max_length=20, unique=True)
    descricao = models.TextField(blank=True)
    cbo = models.CharField(max_length=10, blank=True, help_text='Código Brasileiro de Ocupações')
    nivel = models.CharField(max_length=50, choices=[
        ('estagiario', 'Estagiário'),
        ('junior', 'Júnior'),
        ('pleno', 'Pleno'),
        ('senior', 'Sênior'),
        ('especialista', 'Especialista'),
        ('coordenador', 'Coordenador'),
        ('gerente', 'Gerente'),
        ('diretor', 'Diretor'),
    ], default='pleno')
    salario_base = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    departamento = models.ForeignKey(Departamento, on_delete=models.SET_NULL, null=True, related_name='cargos')
    
    class Meta:
        verbose_name = 'Cargo'
        verbose_name_plural = 'Cargos'
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} ({self.nivel})"


class EscalaTrabalho(BaseModel):
    """Escalas de trabalho personalizadas"""
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    tipo = models.CharField(max_length=50, choices=[
        ('5x2', '5x2 (Seg-Sex)'),
        ('6x1', '6x1'),
        ('12x36', '12x36'),
        ('plantao', 'Plantão'),
        ('flexivel', 'Horário Flexível'),
        ('personalizado', 'Personalizado'),
    ], default='5x2')
    
    # Horários padrão
    hora_entrada = models.TimeField(null=True, blank=True)
    hora_saida = models.TimeField(null=True, blank=True)
    hora_almoco_inicio = models.TimeField(null=True, blank=True)
    hora_almoco_fim = models.TimeField(null=True, blank=True)
    
    # Tolerâncias
    tolerancia_entrada = models.IntegerField(default=10, help_text='Minutos de tolerância na entrada')
    tolerancia_saida = models.IntegerField(default=10, help_text='Minutos de tolerância na saída')
    
    # Configurações
    permite_banco_horas = models.BooleanField(default=True)
    horas_semanais = models.DecimalField(max_digits=4, decimal_places=2, default=44.0)
    
    class Meta:
        verbose_name = 'Escala de Trabalho'
        verbose_name_plural = 'Escalas de Trabalho'
    
    def __str__(self):
        return self.nome


class RegistroPonto(BaseModel):
    """Registro de ponto dos colaboradores"""
    colaborador = models.ForeignKey(Colaborador, on_delete=models.CASCADE, related_name='registros_ponto')
    data = models.DateField(db_index=True)
    
    # Registros
    entrada = models.DateTimeField(null=True, blank=True)
    saida_almoco = models.DateTimeField(null=True, blank=True)
    retorno_almoco = models.DateTimeField(null=True, blank=True)
    saida = models.DateTimeField(null=True, blank=True)
    
    # Metadados
    tipo_registro = models.CharField(max_length=30, choices=[
        ('manual', 'Manual'),
        ('biometria', 'Biometria'),
        ('facial', 'Reconhecimento Facial'),
        ('app', 'Aplicativo Mobile'),
        ('web', 'Portal Web'),
    ], default='web')
    
    # Geolocalização
    latitude_entrada = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitude_entrada = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    latitude_saida = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitude_saida = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    
    # Validações
    foto_entrada = models.ImageField(upload_to='ponto/fotos/', null=True, blank=True)
    foto_saida = models.ImageField(upload_to='ponto/fotos/', null=True, blank=True)
    validado_facial = models.BooleanField(default=False)
    
    # Cálculos
    horas_trabalhadas = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    horas_extras = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    horas_faltantes = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Status
    status = models.CharField(max_length=30, choices=[
        ('pendente', 'Pendente'),
        ('aprovado', 'Aprovado'),
        ('rejeitado', 'Rejeitado'),
        ('ajustado', 'Ajustado'),
    ], default='pendente')
    
    # Assinatura eletrônica
    assinado_colaborador = models.BooleanField(default=False)
    assinado_gestor = models.BooleanField(default=False)
    data_assinatura = models.DateTimeField(null=True, blank=True)
    
    observacao = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Registro de Ponto'
        verbose_name_plural = 'Registros de Ponto'
        ordering = ['-data', 'colaborador']
        unique_together = ['colaborador', 'data']
    
    def __str__(self):
        return f"{self.colaborador.nome_completo} - {self.data}"


class JustificativaPonto(BaseModel):
    """Justificativas para ausências ou ajustes"""
    registro = models.ForeignKey(RegistroPonto, on_delete=models.CASCADE, related_name='justificativas')
    tipo = models.CharField(max_length=50, choices=[
        ('atestado', 'Atestado Médico'),
        ('falta_justificada', 'Falta Justificada'),
        ('falta_injustificada', 'Falta Injustificada'),
        ('atraso', 'Atraso'),
        ('saida_antecipada', 'Saída Antecipada'),
        ('home_office', 'Home Office'),
        ('viagem', 'Viagem a Trabalho'),
        ('outros', 'Outros'),
    ])
    descricao = models.TextField()
    documento = models.FileField(upload_to='justificativas/', null=True, blank=True)
    aprovado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    data_aprovacao = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Justificativa de Ponto'
        verbose_name_plural = 'Justificativas de Ponto'
    
    def __str__(self):
        return f"{self.registro} - {self.tipo}"


# =====================================================
# FOLHA DE PAGAMENTO DIGITAL
# =====================================================

class FolhaPagamento(BaseModel):
    """Folha de pagamento mensal"""
    colaborador = models.ForeignKey(Colaborador, on_delete=models.CASCADE, related_name='folhas_pagamento')
    competencia = models.DateField(help_text='Mês/Ano de referência')
    
    # Valores
    salario_base = models.DecimalField(max_digits=10, decimal_places=2)
    horas_extras = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    adicional_noturno = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    comissoes = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    outros_proventos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Descontos
    inss = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    irrf = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    vale_transporte = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    vale_alimentacao = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    plano_saude = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    emprestimos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    faltas = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    outros_descontos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Totais
    total_proventos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_descontos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    salario_liquido = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # eSocial
    esocial_enviado = models.BooleanField(default=False)
    esocial_protocolo = models.CharField(max_length=100, blank=True)
    esocial_data_envio = models.DateTimeField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=30, choices=[
        ('rascunho', 'Rascunho'),
        ('calculada', 'Calculada'),
        ('aprovada', 'Aprovada'),
        ('paga', 'Paga'),
        ('cancelada', 'Cancelada'),
    ], default='rascunho')
    
    data_pagamento = models.DateField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Folha de Pagamento'
        verbose_name_plural = 'Folhas de Pagamento'
        ordering = ['-competencia', 'colaborador']
        unique_together = ['colaborador', 'competencia']
    
    def __str__(self):
        return f"{self.colaborador.nome_completo} - {self.competencia.strftime('%m/%Y')}"
    
    def calcular_totais(self):
        """Calcula os totais da folha"""
        self.total_proventos = (
            self.salario_base + self.horas_extras + self.adicional_noturno +
            self.comissoes + self.bonus + self.outros_proventos
        )
        self.total_descontos = (
            self.inss + self.irrf + self.vale_transporte + self.vale_alimentacao +
            self.plano_saude + self.emprestimos + self.faltas + self.outros_descontos
        )
        self.salario_liquido = self.total_proventos - self.total_descontos
        self.save()


# =====================================================
# ADMISSÃO DIGITAL
# =====================================================

class ProcessoAdmissao(BaseModel):
    """Processo de admissão digital"""
    candidato_nome = models.CharField(max_length=255)
    candidato_email = models.EmailField()
    candidato_cpf = models.CharField(max_length=14)
    candidato_telefone = models.CharField(max_length=20, blank=True)
    
    cargo_pretendido = models.ForeignKey(Cargo, on_delete=models.SET_NULL, null=True)
    departamento = models.ForeignKey(Departamento, on_delete=models.SET_NULL, null=True)
    data_prevista_admissao = models.DateField()
    salario_proposto = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Status do processo
    status = models.CharField(max_length=30, choices=[
        ('aguardando_documentos', 'Aguardando Documentos'),
        ('documentos_enviados', 'Documentos Enviados'),
        ('em_analise', 'Em Análise'),
        ('pendente_assinatura', 'Pendente Assinatura'),
        ('assinado', 'Contrato Assinado'),
        ('concluido', 'Concluído'),
        ('cancelado', 'Cancelado'),
    ], default='aguardando_documentos')
    
    # Link de preenchimento
    token_acesso = models.CharField(max_length=100, unique=True)
    link_enviado_em = models.DateTimeField(null=True, blank=True)
    
    # Responsável
    responsavel = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='admissoes_responsavel')
    
    # Colaborador criado após conclusão
    colaborador_criado = models.OneToOneField(Colaborador, on_delete=models.SET_NULL, null=True, blank=True)
    
    observacoes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Processo de Admissão'
        verbose_name_plural = 'Processos de Admissão'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.candidato_nome} - {self.status}"


class DocumentoAdmissao(BaseModel):
    """Documentos do processo de admissão"""
    processo = models.ForeignKey(ProcessoAdmissao, on_delete=models.CASCADE, related_name='documentos')
    tipo = models.CharField(max_length=50, choices=[
        ('rg', 'RG'),
        ('cpf', 'CPF'),
        ('ctps', 'CTPS'),
        ('titulo_eleitor', 'Título de Eleitor'),
        ('certificado_reservista', 'Certificado de Reservista'),
        ('comprovante_residencia', 'Comprovante de Residência'),
        ('comprovante_escolaridade', 'Comprovante de Escolaridade'),
        ('foto_3x4', 'Foto 3x4'),
        ('exame_admissional', 'Exame Admissional'),
        ('certidao_nascimento', 'Certidão de Nascimento'),
        ('certidao_casamento', 'Certidão de Casamento'),
        ('pis', 'PIS/PASEP'),
        ('outros', 'Outros'),
    ])
    arquivo = models.FileField(upload_to='admissao/documentos/')
    nome_arquivo = models.CharField(max_length=255)
    validado = models.BooleanField(default=False)
    validado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    data_validacao = models.DateTimeField(null=True, blank=True)
    observacao = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Documento de Admissão'
        verbose_name_plural = 'Documentos de Admissão'
    
    def __str__(self):
        return f"{self.processo.candidato_nome} - {self.tipo}"


# =====================================================
# GESTÃO ELETRÔNICA DE DOCUMENTOS (GED)
# =====================================================

class CategoriaDocumento(BaseModel):
    """Categorias para organização de documentos"""
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    cor = models.CharField(max_length=7, default='#3498db', help_text='Cor em hexadecimal')
    icone = models.CharField(max_length=50, default='file', help_text='Nome do ícone')
    
    class Meta:
        verbose_name = 'Categoria de Documento'
        verbose_name_plural = 'Categorias de Documentos'
    
    def __str__(self):
        return self.nome


class DocumentoGED(BaseModel):
    """Documentos armazenados no GED"""
    titulo = models.CharField(max_length=255)
    descricao = models.TextField(blank=True)
    categoria = models.ForeignKey(CategoriaDocumento, on_delete=models.SET_NULL, null=True, related_name='documentos')
    colaborador = models.ForeignKey(Colaborador, on_delete=models.CASCADE, null=True, blank=True, related_name='documentos_ged')
    
    # Arquivo
    arquivo = models.FileField(upload_to='ged/documentos/')
    nome_arquivo = models.CharField(max_length=255)
    tipo_arquivo = models.CharField(max_length=50, blank=True)
    tamanho_arquivo = models.BigIntegerField(default=0)
    
    # Versionamento
    versao = models.IntegerField(default=1)
    documento_pai = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='versoes')
    
    # Controle de vencimento
    data_vencimento = models.DateField(null=True, blank=True)
    alerta_vencimento_dias = models.IntegerField(default=30, help_text='Dias antes do vencimento para alertar')
    
    # Assinatura digital
    assinado_digitalmente = models.BooleanField(default=False)
    assinatura_hash = models.CharField(max_length=255, blank=True)
    assinado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='documentos_assinados')
    data_assinatura = models.DateTimeField(null=True, blank=True)
    
    # Compartilhamento
    publico = models.BooleanField(default=False)
    compartilhado_com = models.ManyToManyField(User, blank=True, related_name='documentos_compartilhados')
    
    # Metadados
    tags = models.JSONField(default=list, blank=True)
    upload_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='documentos_uploaded')
    
    class Meta:
        verbose_name = 'Documento GED'
        verbose_name_plural = 'Documentos GED'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.titulo


# =====================================================
# GESTÃO DE FÉRIAS
# =====================================================

class PeriodoAquisitivo(BaseModel):
    """Períodos aquisitivos de férias"""
    colaborador = models.ForeignKey(Colaborador, on_delete=models.CASCADE, related_name='periodos_aquisitivos')
    data_inicio = models.DateField()
    data_fim = models.DateField()
    dias_direito = models.IntegerField(default=30)
    dias_gozados = models.IntegerField(default=0)
    dias_vendidos = models.IntegerField(default=0)
    dias_restantes = models.IntegerField(default=30)
    
    # Vencimento
    data_limite_gozo = models.DateField(help_text='Data limite para gozar as férias')
    vencido = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Período Aquisitivo'
        verbose_name_plural = 'Períodos Aquisitivos'
        ordering = ['-data_inicio']
    
    def __str__(self):
        return f"{self.colaborador.nome_completo} - {self.data_inicio} a {self.data_fim}"


class SolicitacaoFerias(BaseModel):
    """Solicitações de férias"""
    colaborador = models.ForeignKey(Colaborador, on_delete=models.CASCADE, related_name='solicitacoes_ferias')
    periodo_aquisitivo = models.ForeignKey(PeriodoAquisitivo, on_delete=models.CASCADE, related_name='solicitacoes')
    
    data_inicio = models.DateField()
    data_fim = models.DateField()
    dias_solicitados = models.IntegerField()
    
    # Abono pecuniário (venda de férias)
    vender_dias = models.IntegerField(default=0, validators=[MaxValueValidator(10)])
    valor_abono = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Adiantamento 13º
    adiantar_13 = models.BooleanField(default=False)
    
    # Status
    status = models.CharField(max_length=30, choices=[
        ('rascunho', 'Rascunho'),
        ('pendente', 'Pendente Aprovação'),
        ('aprovado_gestor', 'Aprovado pelo Gestor'),
        ('aprovado_dp', 'Aprovado pelo DP'),
        ('rejeitado', 'Rejeitado'),
        ('cancelado', 'Cancelado'),
        ('em_gozo', 'Em Gozo'),
        ('concluido', 'Concluído'),
    ], default='rascunho')
    
    # Aprovações
    aprovado_gestor_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='ferias_aprovadas_gestor')
    data_aprovacao_gestor = models.DateTimeField(null=True, blank=True)
    aprovado_dp_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='ferias_aprovadas_dp')
    data_aprovacao_dp = models.DateTimeField(null=True, blank=True)
    
    motivo_rejeicao = models.TextField(blank=True)
    observacoes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Solicitação de Férias'
        verbose_name_plural = 'Solicitações de Férias'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.colaborador.nome_completo} - {self.data_inicio} a {self.data_fim}"


class FeriasColetivas(BaseModel):
    """Férias coletivas"""
    titulo = models.CharField(max_length=255)
    data_inicio = models.DateField()
    data_fim = models.DateField()
    dias = models.IntegerField()
    
    # Abrangência
    todos_colaboradores = models.BooleanField(default=False)
    departamentos = models.ManyToManyField(Departamento, blank=True, related_name='ferias_coletivas')
    colaboradores_excluidos = models.ManyToManyField(Colaborador, blank=True, related_name='excluido_ferias_coletivas')
    
    # Status
    status = models.CharField(max_length=30, choices=[
        ('planejada', 'Planejada'),
        ('comunicada', 'Comunicada'),
        ('em_vigor', 'Em Vigor'),
        ('concluida', 'Concluída'),
        ('cancelada', 'Cancelada'),
    ], default='planejada')
    
    observacoes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Férias Coletivas'
        verbose_name_plural = 'Férias Coletivas'
    
    def __str__(self):
        return f"{self.titulo} - {self.data_inicio} a {self.data_fim}"


# =====================================================
# INTEGRAÇÃO CONTÁBIL
# =====================================================

class Contador(BaseModel):
    """Cadastro de contadores/escritórios contábeis"""
    nome = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=18, blank=True)
    crc = models.CharField(max_length=20, blank=True, help_text='Registro no CRC')
    email = models.EmailField()
    telefone = models.CharField(max_length=20, blank=True)
    
    # Acesso ao sistema
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='contador')
    token_acesso = models.CharField(max_length=100, blank=True)
    
    class Meta:
        verbose_name = 'Contador'
        verbose_name_plural = 'Contadores'
    
    def __str__(self):
        return self.nome


class ExportacaoContabil(BaseModel):
    """Exportações para o contador"""
    contador = models.ForeignKey(Contador, on_delete=models.CASCADE, related_name='exportacoes')
    competencia = models.DateField()
    tipo = models.CharField(max_length=50, choices=[
        ('folha', 'Folha de Pagamento'),
        ('ponto', 'Relatório de Ponto'),
        ('ferias', 'Relatório de Férias'),
        ('admissoes', 'Admissões'),
        ('demissoes', 'Demissões'),
        ('esocial', 'Arquivo eSocial'),
        ('completo', 'Pacote Completo'),
    ])
    
    arquivo = models.FileField(upload_to='contabil/exportacoes/', null=True, blank=True)
    formato = models.CharField(max_length=20, choices=[
        ('pdf', 'PDF'),
        ('xlsx', 'Excel'),
        ('csv', 'CSV'),
        ('xml', 'XML'),
        ('txt', 'TXT'),
    ], default='xlsx')
    
    # Status
    status = models.CharField(max_length=30, choices=[
        ('gerando', 'Gerando'),
        ('disponivel', 'Disponível'),
        ('baixado', 'Baixado'),
        ('erro', 'Erro'),
    ], default='gerando')
    
    baixado_em = models.DateTimeField(null=True, blank=True)
    erro_mensagem = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Exportação Contábil'
        verbose_name_plural = 'Exportações Contábeis'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.tipo} - {self.competencia.strftime('%m/%Y')}"
