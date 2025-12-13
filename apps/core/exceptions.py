"""
SyncRH - Exceções Customizadas
==============================
Exceções padronizadas para tratamento de erros consistente
"""

from rest_framework import status
from rest_framework.exceptions import APIException


class SyncRHBaseException(APIException):
    """Exceção base para todas as exceções do SyncRH"""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Ocorreu um erro interno.'
    default_code = 'server_error'


class ValidationError(SyncRHBaseException):
    """Erro de validação de dados"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Dados inválidos.'
    default_code = 'validation_error'


class BusinessRuleError(SyncRHBaseException):
    """Erro de regra de negócio"""
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = 'Operação não permitida por regra de negócio.'
    default_code = 'business_rule_error'


class ResourceNotFoundError(SyncRHBaseException):
    """Recurso não encontrado"""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Recurso não encontrado.'
    default_code = 'not_found'


class DuplicateResourceError(SyncRHBaseException):
    """Recurso duplicado"""
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Recurso já existe.'
    default_code = 'duplicate'


class PermissionDeniedError(SyncRHBaseException):
    """Permissão negada"""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Você não tem permissão para realizar esta ação.'
    default_code = 'permission_denied'


class AuthenticationError(SyncRHBaseException):
    """Erro de autenticação"""
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Credenciais inválidas.'
    default_code = 'authentication_error'


class IntegrationError(SyncRHBaseException):
    """Erro de integração com sistema externo"""
    status_code = status.HTTP_502_BAD_GATEWAY
    default_detail = 'Erro ao comunicar com sistema externo.'
    default_code = 'integration_error'


class ServiceUnavailableError(SyncRHBaseException):
    """Serviço indisponível"""
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'Serviço temporariamente indisponível.'
    default_code = 'service_unavailable'


class RateLimitExceededError(SyncRHBaseException):
    """Limite de requisições excedido"""
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = 'Limite de requisições excedido. Tente novamente mais tarde.'
    default_code = 'rate_limit_exceeded'


# Exceções específicas de domínio

class ColaboradorNotFoundError(ResourceNotFoundError):
    """Colaborador não encontrado"""
    default_detail = 'Colaborador não encontrado.'
    default_code = 'colaborador_not_found'


class VagaNotFoundError(ResourceNotFoundError):
    """Vaga não encontrada"""
    default_detail = 'Vaga não encontrada.'
    default_code = 'vaga_not_found'


class CandidaturaExistsError(DuplicateResourceError):
    """Candidatura já existe"""
    default_detail = 'Já existe uma candidatura ativa para esta vaga.'
    default_code = 'candidatura_exists'


class FeriasIndisponiveisError(BusinessRuleError):
    """Férias não disponíveis"""
    default_detail = 'Saldo de férias insuficiente ou período indisponível.'
    default_code = 'ferias_indisponiveis'


class PeriodoAquisitivoInvalidoError(BusinessRuleError):
    """Período aquisitivo inválido"""
    default_detail = 'Período aquisitivo de férias não completado.'
    default_code = 'periodo_aquisitivo_invalido'


class FolhaPagamentoBloqueadaError(BusinessRuleError):
    """Folha de pagamento bloqueada"""
    default_detail = 'Folha de pagamento já foi fechada e não pode ser alterada.'
    default_code = 'folha_bloqueada'


class DocumentoExpiradoError(BusinessRuleError):
    """Documento expirado"""
    default_detail = 'Documento expirado ou com data de validade ultrapassada.'
    default_code = 'documento_expirado'


class CicloAvaliacaoFechadoError(BusinessRuleError):
    """Ciclo de avaliação fechado"""
    default_detail = 'Ciclo de avaliação está fechado para novas avaliações.'
    default_code = 'ciclo_fechado'


class PDIJaConcuidoError(BusinessRuleError):
    """PDI já concluído"""
    default_detail = 'PDI já está concluído e não pode ser alterado.'
    default_code = 'pdi_concluido'


class CursoNaoDisponivelError(BusinessRuleError):
    """Curso não disponível"""
    default_detail = 'Curso não está disponível para matrícula.'
    default_code = 'curso_nao_disponivel'


class PreRequisitosNaoAtendidosError(BusinessRuleError):
    """Pré-requisitos não atendidos"""
    default_detail = 'Pré-requisitos do curso não foram atendidos.'
    default_code = 'pre_requisitos'


class QuestionarioJaRespondidoError(BusinessRuleError):
    """Questionário já respondido"""
    default_detail = 'Este questionário já foi respondido.'
    default_code = 'questionario_respondido'


class AplicacaoNaoFinalizadaError(BusinessRuleError):
    """Aplicação do profiler não finalizada"""
    default_detail = 'A aplicação do questionário não foi finalizada corretamente.'
    default_code = 'aplicacao_nao_finalizada'


class BeneficioNaoElegivelError(BusinessRuleError):
    """Não elegível para o benefício"""
    default_detail = 'Colaborador não é elegível para este benefício.'
    default_code = 'beneficio_nao_elegivel'


class PromocaoJaAprovadaError(BusinessRuleError):
    """Promoção já aprovada"""
    default_detail = 'Solicitação de promoção já foi aprovada.'
    default_code = 'promocao_aprovada'


# Handler de exceções customizado para Django REST Framework

def custom_exception_handler(exc, context):
    """
    Handler customizado de exceções.
    
    Padroniza o formato de resposta de erros para:
    {
        "error": "Código do erro",
        "detail": "Descrição do erro",
        "errors": [...] // opcional, para erros de validação múltiplos
    }
    """
    from rest_framework.views import exception_handler
    
    # Chama o handler padrão primeiro
    response = exception_handler(exc, context)
    
    if response is not None:
        # Padroniza formato
        error_data = {
            'error': getattr(exc, 'default_code', 'error'),
            'detail': response.data.get('detail', str(exc))
        }
        
        # Para erros de validação do DRF
        if isinstance(response.data, dict) and 'detail' not in response.data:
            error_data['errors'] = response.data
            error_data['detail'] = 'Erro de validação dos dados enviados.'
        
        response.data = error_data
    
    return response
