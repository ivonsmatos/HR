"""
SyncRH - Serviços LGPD
======================
Serviços para operações de conformidade com LGPD
"""

from django.db import transaction
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


class AnonimizacaoService:
    """
    Serviço para anonimização e pseudonimização de dados pessoais.
    Implementa técnicas conforme Art. 5, XI da LGPD.
    """
    
    # Técnicas de anonimização
    TECNICAS = {
        'hash': 'Hash SHA-256',
        'generalizacao': 'Generalização',
        'supressao': 'Supressão',
        'mascaramento': 'Mascaramento',
        'perturbacao': 'Perturbação',
        'troca': 'Troca de Valores',
    }
    
    @staticmethod
    def anonimizar_cpf(cpf: str) -> str:
        """Anonimiza CPF mantendo apenas os 3 primeiros dígitos"""
        if not cpf:
            return ''
        cpf_limpo = ''.join(filter(str.isdigit, cpf))
        return f"{cpf_limpo[:3]}.***.***-**"
    
    @staticmethod
    def anonimizar_email(email: str) -> str:
        """Anonimiza email mantendo domínio"""
        if not email or '@' not in email:
            return ''
        local, domain = email.split('@')
        if len(local) <= 2:
            return f"**@{domain}"
        return f"{local[0]}***{local[-1]}@{domain}"
    
    @staticmethod
    def anonimizar_telefone(telefone: str) -> str:
        """Anonimiza telefone mantendo DDD"""
        if not telefone:
            return ''
        numeros = ''.join(filter(str.isdigit, telefone))
        if len(numeros) >= 2:
            return f"({numeros[:2]}) *****-****"
        return "(**) *****-****"
    
    @staticmethod
    def anonimizar_nome(nome: str) -> str:
        """Anonimiza nome mantendo iniciais"""
        if not nome:
            return ''
        partes = nome.split()
        return ' '.join(f"{p[0]}." if len(p) > 1 else p for p in partes)
    
    @staticmethod
    def pseudonimizar(valor: str, salt: str = '') -> str:
        """Pseudonimiza valor usando hash (reversível com chave)"""
        if not valor:
            return ''
        data = f"{valor}{salt}{settings.SECRET_KEY}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    @staticmethod
    def hash_irreversivel(valor: str) -> str:
        """Hash irreversível para anonimização completa"""
        if not valor:
            return ''
        return hashlib.sha256(valor.encode()).hexdigest()
    
    @classmethod
    @transaction.atomic
    def anonimizar_colaborador(cls, colaborador, motivo: str, executado_por):
        """
        Anonimiza todos os dados pessoais de um colaborador.
        Usado quando colaborador exerce direito de eliminação.
        """
        from .models import RegistroAnonimizacao
        
        campos_anonimizados = []
        
        # Anonimiza dados de identificação
        if colaborador.cpf:
            colaborador.cpf = cls.hash_irreversivel(colaborador.cpf)
            campos_anonimizados.append('cpf')
        
        if colaborador.nome_completo:
            colaborador.nome_completo = f"Usuário Anonimizado {colaborador.id}"
            campos_anonimizados.append('nome_completo')
        
        if hasattr(colaborador, 'email_pessoal') and colaborador.email_pessoal:
            colaborador.email_pessoal = ''
            campos_anonimizados.append('email_pessoal')
        
        if hasattr(colaborador, 'telefone') and colaborador.telefone:
            colaborador.telefone = ''
            campos_anonimizados.append('telefone')
        
        if hasattr(colaborador, 'endereco') and colaborador.endereco:
            colaborador.endereco = ''
            campos_anonimizados.append('endereco')
        
        # Dados bancários
        if hasattr(colaborador, 'conta') and colaborador.conta:
            colaborador.conta = ''
            colaborador.agencia = ''
            colaborador.banco = ''
            campos_anonimizados.extend(['conta', 'agencia', 'banco'])
        
        colaborador.save()
        
        # Registra operação
        RegistroAnonimizacao.objects.create(
            tipo='anonimizacao',
            motivo=motivo,
            descricao=f'Anonimização de colaborador ID {colaborador.id}',
            modelo='Colaborador',
            campos=campos_anonimizados,
            quantidade_registros=1,
            executado_por=executado_por,
            tecnica='hash + supressao',
            reversivel=False
        )
        
        logger.info(f"Colaborador {colaborador.id} anonimizado por {executado_por}")
        
        return campos_anonimizados


class PortabilidadeService:
    """
    Serviço para portabilidade de dados (Art. 18, V da LGPD).
    """
    
    @staticmethod
    def exportar_dados_titular(titular, formato='json'):
        """
        Exporta todos os dados pessoais do titular em formato estruturado.
        """
        dados = {
            'informacoes_gerais': {
                'data_exportacao': timezone.now().isoformat(),
                'formato': formato,
                'titular_id': titular.id,
            },
            'dados_pessoais': {},
            'consentimentos': [],
            'solicitacoes': [],
        }
        
        # Dados do usuário
        dados['dados_pessoais']['usuario'] = {
            'username': titular.username,
            'email': titular.email,
            'first_name': titular.first_name,
            'last_name': titular.last_name,
            'date_joined': titular.date_joined.isoformat() if titular.date_joined else None,
            'last_login': titular.last_login.isoformat() if titular.last_login else None,
        }
        
        # Dados de colaborador se existir
        if hasattr(titular, 'colaborador'):
            col = titular.colaborador
            dados['dados_pessoais']['colaborador'] = {
                'nome_completo': col.nome_completo,
                'cpf': AnonimizacaoService.anonimizar_cpf(col.cpf),
                'data_nascimento': str(col.data_nascimento) if col.data_nascimento else None,
                'data_admissao': str(col.data_admissao) if col.data_admissao else None,
                'cargo': str(col.cargo) if col.cargo else None,
                'departamento': str(col.departamento) if col.departamento else None,
            }
        
        # Consentimentos
        from .models import ConsentimentoTitular
        consentimentos = ConsentimentoTitular.objects.filter(titular=titular)
        for c in consentimentos:
            dados['consentimentos'].append({
                'termo': c.termo.titulo,
                'versao': c.termo.versao,
                'data_consentimento': c.data_consentimento.isoformat(),
                'ativo': c.esta_ativo,
                'finalidades': c.finalidades_aceitas,
            })
        
        # Solicitações LGPD
        from .models import SolicitacaoTitular
        solicitacoes = SolicitacaoTitular.objects.filter(titular=titular)
        for s in solicitacoes:
            dados['solicitacoes'].append({
                'protocolo': s.protocolo,
                'tipo': s.get_tipo_display(),
                'status': s.get_status_display(),
                'data': s.created_at.isoformat(),
            })
        
        if formato == 'json':
            return json.dumps(dados, indent=2, ensure_ascii=False)
        
        return dados


class SolicitacaoService:
    """
    Serviço para gestão de solicitações dos titulares.
    """
    
    @staticmethod
    @transaction.atomic
    def criar_solicitacao(titular, tipo, descricao, email_contato=None):
        """Cria nova solicitação do titular"""
        from .models import SolicitacaoTitular
        
        solicitacao = SolicitacaoTitular.objects.create(
            titular=titular,
            tipo=tipo,
            descricao=descricao,
            email_contato=email_contato or titular.email
        )
        
        # Notifica DPO
        SolicitacaoService._notificar_dpo(solicitacao)
        
        # Notifica titular
        SolicitacaoService._notificar_titular(solicitacao, 'criacao')
        
        return solicitacao
    
    @staticmethod
    def processar_solicitacao(solicitacao, responsavel, resposta, status='concluida'):
        """Processa e responde solicitação"""
        solicitacao.responsavel = responsavel
        solicitacao.resposta = resposta
        solicitacao.status = status
        solicitacao.data_resposta = timezone.now()
        solicitacao.save()
        
        # Notifica titular
        SolicitacaoService._notificar_titular(solicitacao, 'resposta')
        
        return solicitacao
    
    @staticmethod
    def _notificar_dpo(solicitacao):
        """Notifica DPO sobre nova solicitação"""
        try:
            dpo_email = getattr(settings, 'DPO_EMAIL', None)
            if dpo_email:
                send_mail(
                    f'[LGPD] Nova Solicitação - {solicitacao.protocolo}',
                    f'Nova solicitação de {solicitacao.get_tipo_display()} registrada.\n'
                    f'Protocolo: {solicitacao.protocolo}\n'
                    f'Prazo: {solicitacao.data_limite}',
                    settings.DEFAULT_FROM_EMAIL,
                    [dpo_email],
                    fail_silently=True
                )
        except Exception as e:
            logger.error(f"Erro ao notificar DPO: {e}")
    
    @staticmethod
    def _notificar_titular(solicitacao, tipo):
        """Notifica titular sobre sua solicitação"""
        try:
            assuntos = {
                'criacao': f'Solicitação Recebida - {solicitacao.protocolo}',
                'resposta': f'Sua Solicitação foi Respondida - {solicitacao.protocolo}',
            }
            
            mensagens = {
                'criacao': f'Sua solicitação foi registrada com sucesso.\n'
                          f'Protocolo: {solicitacao.protocolo}\n'
                          f'Tipo: {solicitacao.get_tipo_display()}\n'
                          f'Prazo para resposta: {solicitacao.data_limite.strftime("%d/%m/%Y")}',
                'resposta': f'Sua solicitação foi processada.\n'
                           f'Protocolo: {solicitacao.protocolo}\n'
                           f'Status: {solicitacao.get_status_display()}\n'
                           f'Resposta: {solicitacao.resposta}',
            }
            
            send_mail(
                assuntos[tipo],
                mensagens[tipo],
                settings.DEFAULT_FROM_EMAIL,
                [solicitacao.email_contato],
                fail_silently=True
            )
        except Exception as e:
            logger.error(f"Erro ao notificar titular: {e}")


class IncidenteService:
    """
    Serviço para gestão de incidentes de segurança com dados pessoais.
    """
    
    @staticmethod
    def registrar_incidente(dados, reportado_por):
        """Registra novo incidente de segurança"""
        from .models import IncidenteSeguranca
        
        incidente = IncidenteSeguranca.objects.create(
            reportado_por=reportado_por,
            **dados
        )
        
        # Se severidade alta/crítica, notifica automaticamente
        if incidente.severidade in ['alta', 'critica']:
            IncidenteService._notificar_equipe_seguranca(incidente)
        
        return incidente
    
    @staticmethod
    def comunicar_anpd(incidente, protocolo_anpd=None):
        """Registra comunicação à ANPD"""
        incidente.comunicado_anpd = True
        incidente.data_comunicacao_anpd = timezone.now()
        if protocolo_anpd:
            incidente.protocolo_anpd = protocolo_anpd
        incidente.save()
        
        logger.info(f"Incidente {incidente.protocolo} comunicado à ANPD")
        return incidente
    
    @staticmethod
    def comunicar_titulares(incidente, metodo='email'):
        """Registra comunicação aos titulares afetados"""
        incidente.comunicado_titulares = True
        incidente.data_comunicacao_titulares = timezone.now()
        incidente.metodo_comunicacao_titulares = metodo
        incidente.save()
        
        return incidente
    
    @staticmethod
    def _notificar_equipe_seguranca(incidente):
        """Notifica equipe de segurança sobre incidente grave"""
        try:
            security_email = getattr(settings, 'SECURITY_TEAM_EMAIL', None)
            if security_email:
                send_mail(
                    f'[ALERTA] Incidente de Segurança - {incidente.protocolo}',
                    f'Incidente de segurança detectado.\n'
                    f'Severidade: {incidente.get_severidade_display()}\n'
                    f'Tipo: {incidente.get_tipo_incidente_display()}\n'
                    f'Descrição: {incidente.descricao}\n',
                    settings.DEFAULT_FROM_EMAIL,
                    [security_email],
                    fail_silently=True
                )
        except Exception as e:
            logger.error(f"Erro ao notificar equipe de segurança: {e}")


class ConsentimentoService:
    """
    Serviço para gestão de consentimentos.
    """
    
    @staticmethod
    def registrar_consentimento(titular, termo, finalidades, request):
        """Registra consentimento do titular"""
        from .models import ConsentimentoTitular
        
        consentimento = ConsentimentoTitular.objects.create(
            titular=titular,
            termo=termo,
            finalidades_aceitas=finalidades,
            ip_address=ConsentimentoService._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        logger.info(f"Consentimento registrado: {titular} - {termo.titulo}")
        return consentimento
    
    @staticmethod
    def revogar_consentimento(consentimento, motivo=''):
        """Revoga consentimento existente"""
        consentimento.revogar(motivo)
        
        logger.info(f"Consentimento revogado: {consentimento.titular} - {consentimento.termo.titulo}")
        return consentimento
    
    @staticmethod
    def verificar_consentimento(titular, finalidade):
        """Verifica se titular tem consentimento ativo para finalidade"""
        from .models import ConsentimentoTitular
        
        return ConsentimentoTitular.objects.filter(
            titular=titular,
            finalidades_aceitas__contains=finalidade,
            data_revogacao__isnull=True,
            termo__data_vigencia_inicio__lte=timezone.now().date(),
        ).filter(
            models.Q(termo__data_vigencia_fim__isnull=True) |
            models.Q(termo__data_vigencia_fim__gte=timezone.now().date())
        ).exists()
    
    @staticmethod
    def _get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '0.0.0.0')
