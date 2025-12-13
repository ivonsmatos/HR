"""
SyncRH - Constantes e Choices
=============================

Constantes e choices utilizados em toda a aplicação.
Centraliza definições para manter consistência.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


# =====================================================
# STATUS GENÉRICOS
# =====================================================

class StatusGeral(models.TextChoices):
    """Status genérico para registros"""
    RASCUNHO = 'rascunho', _('Rascunho')
    ATIVO = 'ativo', _('Ativo')
    INATIVO = 'inativo', _('Inativo')
    ARQUIVADO = 'arquivado', _('Arquivado')


class StatusAprovacao(models.TextChoices):
    """Status de aprovação de processos"""
    PENDENTE = 'pendente', _('Pendente')
    EM_ANALISE = 'em_analise', _('Em Análise')
    APROVADO = 'aprovado', _('Aprovado')
    REPROVADO = 'reprovado', _('Reprovado')
    CANCELADO = 'cancelado', _('Cancelado')


# =====================================================
# DEPARTAMENTO PESSOAL
# =====================================================

class TipoContrato(models.TextChoices):
    """Tipos de contrato de trabalho"""
    CLT = 'clt', _('CLT')
    PJ = 'pj', _('PJ')
    ESTAGIO = 'estagio', _('Estágio')
    TEMPORARIO = 'temporario', _('Temporário')
    APRENDIZ = 'aprendiz', _('Aprendiz')
    INTERMITENTE = 'intermitente', _('Intermitente')


class TipoConta(models.TextChoices):
    """Tipos de conta bancária"""
    CORRENTE = 'corrente', _('Conta Corrente')
    POUPANCA = 'poupanca', _('Conta Poupança')
    SALARIO = 'salario', _('Conta Salário')


class NivelCargo(models.TextChoices):
    """Níveis de cargo"""
    ESTAGIARIO = 'estagiario', _('Estagiário')
    JUNIOR = 'junior', _('Júnior')
    PLENO = 'pleno', _('Pleno')
    SENIOR = 'senior', _('Sênior')
    ESPECIALISTA = 'especialista', _('Especialista')
    COORDENADOR = 'coordenador', _('Coordenador')
    GERENTE = 'gerente', _('Gerente')
    DIRETOR = 'diretor', _('Diretor')
    EXECUTIVO = 'executivo', _('Executivo')


class TipoPonto(models.TextChoices):
    """Tipos de registro de ponto"""
    ENTRADA = 'entrada', _('Entrada')
    SAIDA = 'saída', _('Saída')
    INICIO_INTERVALO = 'inicio_intervalo', _('Início Intervalo')
    FIM_INTERVALO = 'fim_intervalo', _('Fim Intervalo')


class OrigemPonto(models.TextChoices):
    """Origem do registro de ponto"""
    APLICATIVO = 'app', _('Aplicativo')
    WEB = 'web', _('Web')
    RELOGIO = 'relogio', _('Relógio de Ponto')
    MANUAL = 'manual', _('Manual')
    RECONHECIMENTO_FACIAL = 'facial', _('Reconhecimento Facial')


class StatusFerias(models.TextChoices):
    """Status de solicitação de férias"""
    RASCUNHO = 'rascunho', _('Rascunho')
    PENDENTE = 'pendente', _('Pendente Aprovação')
    APROVADO_GESTOR = 'aprovado_gestor', _('Aprovado pelo Gestor')
    APROVADO = 'aprovado', _('Aprovado')
    REJEITADO = 'rejeitado', _('Rejeitado')
    EM_GOZO = 'em_gozo', _('Em Gozo')
    CONCLUIDO = 'concluido', _('Concluído')
    CANCELADO = 'cancelado', _('Cancelado')


# =====================================================
# RECRUTAMENTO E SELEÇÃO
# =====================================================

class StatusVaga(models.TextChoices):
    """Status de vaga"""
    RASCUNHO = 'rascunho', _('Rascunho')
    ABERTA = 'aberta', _('Aberta')
    EM_SELECAO = 'em_selecao', _('Em Seleção')
    SUSPENSA = 'suspensa', _('Suspensa')
    FECHADA = 'fechada', _('Fechada')
    CANCELADA = 'cancelada', _('Cancelada')


class StatusCandidatura(models.TextChoices):
    """Status de candidatura"""
    INSCRITO = 'inscrito', _('Inscrito')
    TRIAGEM = 'triagem', _('Em Triagem')
    ENTREVISTA_RH = 'entrevista_rh', _('Entrevista RH')
    ENTREVISTA_TECNICA = 'entrevista_tecnica', _('Entrevista Técnica')
    ENTREVISTA_GESTOR = 'entrevista_gestor', _('Entrevista Gestor')
    PROPOSTA = 'proposta', _('Proposta')
    CONTRATADO = 'contratado', _('Contratado')
    REPROVADO = 'reprovado', _('Reprovado')
    DESISTENCIA = 'desistencia', _('Desistência')
    BANCO_TALENTOS = 'banco_talentos', _('Banco de Talentos')


class TipoEntrevista(models.TextChoices):
    """Tipos de entrevista"""
    TRIAGEM = 'triagem', _('Triagem')
    RH = 'rh', _('RH')
    TECNICA = 'tecnica', _('Técnica')
    GESTOR = 'gestor', _('Gestor')
    FINAL = 'final', _('Final')
    PAINEL = 'painel', _('Painel')


# =====================================================
# PERFIL COMPORTAMENTAL (DISC)
# =====================================================

class PerfilDISC(models.TextChoices):
    """Perfis DISC"""
    D = 'D', _('Dominância')
    I = 'I', _('Influência')
    S = 'S', _('Estabilidade')
    C = 'C', _('Conformidade')
    DI = 'DI', _('Dominância/Influência')
    DC = 'DC', _('Dominância/Conformidade')
    ID = 'ID', _('Influência/Dominância')
    IS = 'IS', _('Influência/Estabilidade')
    SI = 'SI', _('Estabilidade/Influência')
    SC = 'SC', _('Estabilidade/Conformidade')
    CD = 'CD', _('Conformidade/Dominância')
    CS = 'CS', _('Conformidade/Estabilidade')


# =====================================================
# DESENVOLVIMENTO E PERFORMANCE
# =====================================================

class StatusPDI(models.TextChoices):
    """Status de PDI"""
    RASCUNHO = 'rascunho', _('Rascunho')
    ATIVO = 'ativo', _('Ativo')
    EM_ANDAMENTO = 'em_andamento', _('Em Andamento')
    CONCLUIDO = 'concluido', _('Concluído')
    CANCELADO = 'cancelado', _('Cancelado')


class QuadranteSyncBox(models.TextChoices):
    """Quadrantes do SyncBox (9Box)"""
    ENIGMA = 'enigma', _('Enigma (Alto Potencial, Baixo Desempenho)')
    FORTE_DESEMPENHO = 'forte_desempenho', _('Forte Desempenho')
    ESTRELA = 'estrela', _('Estrela (Alto Potencial, Alto Desempenho)')
    QUESTIONAVEL = 'questionavel', _('Questionável')
    MANTENEDOR = 'mantenedor', _('Mantenedor')
    FORTE_POTENCIAL = 'forte_potencial', _('Forte Potencial')
    INSUFICIENTE = 'insuficiente', _('Insuficiente')
    EFICAZ = 'eficaz', _('Eficaz')
    COMPROMETIDO = 'comprometido', _('Comprometido')


class TipoAvaliacao(models.TextChoices):
    """Tipos de avaliação"""
    AUTOAVALIACAO = 'auto', _('Autoavaliação')
    GESTOR = 'gestor', _('Avaliação do Gestor')
    PARES = 'pares', _('Avaliação de Pares')
    SUBORDINADOS = 'subordinados', _('Avaliação de Subordinados')
    COMPLETA_360 = '360', _('Avaliação 360°')


# =====================================================
# ENGAJAMENTO E RETENÇÃO
# =====================================================

class StatusPesquisa(models.TextChoices):
    """Status de pesquisa"""
    RASCUNHO = 'rascunho', _('Rascunho')
    AGENDADA = 'agendada', _('Agendada')
    EM_ANDAMENTO = 'em_andamento', _('Em Andamento')
    ENCERRADA = 'encerrada', _('Encerrada')
    ANALISADA = 'analisada', _('Analisada')


class ClassificacaoENPS(models.TextChoices):
    """Classificação eNPS"""
    PROMOTOR = 'promotor', _('Promotor (9-10)')
    NEUTRO = 'neutro', _('Neutro (7-8)')
    DETRATOR = 'detrator', _('Detrator (0-6)')


class NivelRisco(models.TextChoices):
    """Níveis de risco de rotatividade"""
    BAIXO = 'baixo', _('Baixo (0-25)')
    MEDIO = 'medio', _('Médio (26-50)')
    ALTO = 'alto', _('Alto (51-75)')
    CRITICO = 'critico', _('Crítico (76-100)')


class TipoDesligamento(models.TextChoices):
    """Tipos de desligamento"""
    VOLUNTARIA = 'voluntaria', _('Demissão Voluntária')
    INVOLUNTARIA = 'involuntaria', _('Demissão Involuntária')
    ACORDO = 'acordo', _('Acordo Mútuo')
    TERMINO_CONTRATO = 'termino_contrato', _('Término de Contrato')
    APOSENTADORIA = 'aposentadoria', _('Aposentadoria')
    FALECIMENTO = 'falecimento', _('Falecimento')


class CategoriaBeneficio(models.TextChoices):
    """Categorias de benefícios"""
    ALIMENTACAO = 'alimentacao', _('Alimentação')
    TRANSPORTE = 'transporte', _('Transporte')
    SAUDE = 'saude', _('Saúde')
    EDUCACAO = 'educacao', _('Educação')
    BEM_ESTAR = 'bem_estar', _('Bem-estar')
    FINANCEIRO = 'financeiro', _('Financeiro')
    OUTROS = 'outros', _('Outros')


# =====================================================
# PRIORIDADES
# =====================================================

class Prioridade(models.TextChoices):
    """Níveis de prioridade"""
    BAIXA = 'baixa', _('Baixa')
    MEDIA = 'media', _('Média')
    ALTA = 'alta', _('Alta')
    CRITICA = 'critica', _('Crítica')


# =====================================================
# GÊNERO E ESTADO CIVIL
# =====================================================

class Genero(models.TextChoices):
    """Gênero"""
    MASCULINO = 'M', _('Masculino')
    FEMININO = 'F', _('Feminino')
    OUTRO = 'O', _('Outro')
    NAO_INFORMADO = 'N', _('Não Informado')


class EstadoCivil(models.TextChoices):
    """Estado civil"""
    SOLTEIRO = 'solteiro', _('Solteiro(a)')
    CASADO = 'casado', _('Casado(a)')
    DIVORCIADO = 'divorciado', _('Divorciado(a)')
    VIUVO = 'viuvo', _('Viúvo(a)')
    UNIAO_ESTAVEL = 'uniao_estavel', _('União Estável')


# =====================================================
# ESTADOS BRASILEIROS
# =====================================================

class UF(models.TextChoices):
    """Unidades Federativas do Brasil"""
    AC = 'AC', _('Acre')
    AL = 'AL', _('Alagoas')
    AP = 'AP', _('Amapá')
    AM = 'AM', _('Amazonas')
    BA = 'BA', _('Bahia')
    CE = 'CE', _('Ceará')
    DF = 'DF', _('Distrito Federal')
    ES = 'ES', _('Espírito Santo')
    GO = 'GO', _('Goiás')
    MA = 'MA', _('Maranhão')
    MT = 'MT', _('Mato Grosso')
    MS = 'MS', _('Mato Grosso do Sul')
    MG = 'MG', _('Minas Gerais')
    PA = 'PA', _('Pará')
    PB = 'PB', _('Paraíba')
    PR = 'PR', _('Paraná')
    PE = 'PE', _('Pernambuco')
    PI = 'PI', _('Piauí')
    RJ = 'RJ', _('Rio de Janeiro')
    RN = 'RN', _('Rio Grande do Norte')
    RS = 'RS', _('Rio Grande do Sul')
    RO = 'RO', _('Rondônia')
    RR = 'RR', _('Roraima')
    SC = 'SC', _('Santa Catarina')
    SP = 'SP', _('São Paulo')
    SE = 'SE', _('Sergipe')
    TO = 'TO', _('Tocantins')
