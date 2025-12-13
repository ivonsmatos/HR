"""
SyncRH - Engajamento e Retenção - Services
==========================================
Camada de serviços com lógica de negócio
"""

from django.db import transaction
from django.db.models import Avg, Count, Q, Sum
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


class PesquisaClimaService:
    """Serviço para gestão de pesquisas de clima"""
    
    @staticmethod
    @transaction.atomic
    def criar_pesquisa(dados):
        """Cria nova pesquisa de clima"""
        from .models import PesquisaClima
        
        pesquisa = PesquisaClima.objects.create(**dados)
        logger.info(f"Pesquisa de clima criada: {pesquisa.titulo}")
        return pesquisa
    
    @staticmethod
    def publicar_pesquisa(pesquisa):
        """Publica pesquisa para respostas"""
        pesquisa.status = 'em_andamento'
        pesquisa.save()
        
        # Notifica colaboradores elegíveis
        PesquisaClimaService._notificar_colaboradores(pesquisa)
        
        return pesquisa
    
    @staticmethod
    def encerrar_pesquisa(pesquisa):
        """Encerra pesquisa e processa resultados"""
        pesquisa.status = 'encerrada'
        pesquisa.save()
        
        # Processa resultados
        PesquisaClimaService._processar_resultados(pesquisa)
        
        return pesquisa
    
    @staticmethod
    def _processar_resultados(pesquisa):
        """Processa e consolida resultados da pesquisa"""
        from .models import ResultadoClima, RespostaClima, PerguntaClima
        
        # Agrupa por categoria
        categorias = PerguntaClima.objects.filter(
            pesquisa=pesquisa
        ).values_list('categoria', flat=True).distinct()
        
        for categoria in categorias:
            perguntas = PerguntaClima.objects.filter(
                pesquisa=pesquisa,
                categoria=categoria
            )
            
            respostas = RespostaClima.objects.filter(
                pergunta__in=perguntas
            )
            
            if respostas.exists():
                media = respostas.aggregate(Avg('nota'))['nota__avg']
                
                ResultadoClima.objects.update_or_create(
                    pesquisa=pesquisa,
                    categoria=categoria,
                    defaults={
                        'media_nota': round(media, 2) if media else 0,
                        'total_respostas': respostas.count()
                    }
                )
    
    @staticmethod
    def _notificar_colaboradores(pesquisa):
        """Notifica colaboradores sobre pesquisa"""
        # Implementação de notificação
        pass
    
    @staticmethod
    def calcular_participacao(pesquisa):
        """Calcula percentual de participação"""
        from .models import RespostaClima
        from apps.departamento_pessoal.models import Colaborador
        
        total_colaboradores = Colaborador.objects.filter(status='ativo').count()
        
        if total_colaboradores == 0:
            return 0
        
        # Conta colaboradores que responderam (baseado em respostas únicas)
        respondentes = RespostaClima.objects.filter(
            pergunta__pesquisa=pesquisa
        ).values('colaborador').distinct().count()
        
        return round((respondentes / total_colaboradores) * 100, 2)


class eNPSService:
    """Serviço para gestão de pesquisas eNPS"""
    
    @staticmethod
    def calcular_enps(pesquisa):
        """Calcula score eNPS"""
        from .models import RespostaeNPS
        
        respostas = RespostaeNPS.objects.filter(pesquisa=pesquisa)
        total = respostas.count()
        
        if total == 0:
            return None
        
        promotores = respostas.filter(nota__gte=9).count()
        detratores = respostas.filter(nota__lte=6).count()
        
        enps = ((promotores - detratores) / total) * 100
        
        return {
            'score': round(enps, 1),
            'total_respostas': total,
            'promotores': promotores,
            'neutros': total - promotores - detratores,
            'detratores': detratores,
            'percentual_promotores': round((promotores / total) * 100, 1),
            'percentual_detratores': round((detratores / total) * 100, 1)
        }
    
    @staticmethod
    def analisar_tendencia(limite_pesquisas=6):
        """Analisa tendência do eNPS ao longo do tempo"""
        from .models import PesquisaeNPS
        
        pesquisas = PesquisaeNPS.objects.filter(
            status='encerrada'
        ).order_by('-data_fim')[:limite_pesquisas]
        
        tendencia = []
        for pesquisa in pesquisas:
            resultado = eNPSService.calcular_enps(pesquisa)
            if resultado:
                tendencia.append({
                    'pesquisa': pesquisa.titulo,
                    'data': pesquisa.data_fim,
                    'score': resultado['score']
                })
        
        return list(reversed(tendencia))
    
    @staticmethod
    def classificar_score(score):
        """Classifica score eNPS"""
        if score >= 50:
            return {'classificacao': 'excelente', 'cor': 'green'}
        elif score >= 0:
            return {'classificacao': 'bom', 'cor': 'blue'}
        elif score >= -50:
            return {'classificacao': 'atencao', 'cor': 'yellow'}
        return {'classificacao': 'critico', 'cor': 'red'}


class BeneficiosService:
    """Serviço para gestão de benefícios"""
    
    @staticmethod
    def atribuir_beneficio(colaborador, tipo_beneficio, dados=None):
        """Atribui benefício a colaborador"""
        from .models import BeneficioColaborador
        
        # Verifica elegibilidade
        if tipo_beneficio.elegibilidade:
            if not BeneficiosService._verificar_elegibilidade(
                colaborador, tipo_beneficio.elegibilidade
            ):
                raise ValueError("Colaborador não elegível para este benefício")
        
        beneficio = BeneficioColaborador.objects.create(
            colaborador=colaborador,
            tipo_beneficio=tipo_beneficio,
            valor=tipo_beneficio.valor_padrao,
            status='ativo',
            data_inicio=timezone.now().date(),
            **(dados or {})
        )
        
        return beneficio
    
    @staticmethod
    def _verificar_elegibilidade(colaborador, criterios):
        """Verifica elegibilidade do colaborador"""
        # Implementação simplificada
        return True
    
    @staticmethod
    def calcular_custo_beneficios(departamento=None, periodo=None):
        """Calcula custo total de benefícios"""
        from .models import BeneficioColaborador
        
        filtros = {'status': 'ativo'}
        
        if departamento:
            filtros['colaborador__departamento'] = departamento
        
        beneficios = BeneficioColaborador.objects.filter(**filtros)
        
        return {
            'total_colaboradores': beneficios.values('colaborador').distinct().count(),
            'custo_total': beneficios.aggregate(Sum('valor'))['valor__sum'] or 0,
            'por_tipo': list(
                beneficios.values('tipo_beneficio__nome').annotate(
                    total=Sum('valor'),
                    quantidade=Count('id')
                )
            )
        }


class PromocaoService:
    """Serviço para gestão de promoções"""
    
    @staticmethod
    @transaction.atomic
    def criar_solicitacao(colaborador, solicitante, dados):
        """Cria solicitação de promoção"""
        from .models import SolicitacaoPromocao
        
        # Calcula percentual de aumento
        if dados.get('salario_atual') and dados.get('salario_proposto'):
            atual = float(dados['salario_atual'])
            proposto = float(dados['salario_proposto'])
            if atual > 0:
                dados['percentual_aumento'] = round(((proposto - atual) / atual) * 100, 2)
        
        solicitacao = SolicitacaoPromocao.objects.create(
            colaborador=colaborador,
            solicitante=solicitante,
            status='pendente',
            **dados
        )
        
        # Notifica aprovadores
        PromocaoService._notificar_aprovadores(solicitacao)
        
        return solicitacao
    
    @staticmethod
    def aprovar_solicitacao(solicitacao, aprovador, parecer):
        """Aprova solicitação de promoção"""
        solicitacao.status = 'aprovada'
        solicitacao.aprovador = aprovador
        solicitacao.parecer_aprovador = parecer
        solicitacao.data_aprovacao = timezone.now()
        solicitacao.save()
        
        # Notifica colaborador e gestor
        PromocaoService._notificar_aprovacao(solicitacao)
        
        return solicitacao
    
    @staticmethod
    def rejeitar_solicitacao(solicitacao, aprovador, parecer):
        """Rejeita solicitação de promoção"""
        solicitacao.status = 'rejeitada'
        solicitacao.aprovador = aprovador
        solicitacao.parecer_aprovador = parecer
        solicitacao.data_aprovacao = timezone.now()
        solicitacao.save()
        
        return solicitacao
    
    @staticmethod
    def efetivar_promocao(solicitacao):
        """Efetiva a promoção aprovada"""
        if solicitacao.status != 'aprovada':
            raise ValueError("Solicitação não está aprovada")
        
        colaborador = solicitacao.colaborador
        
        # Atualiza cargo e salário
        colaborador.cargo = solicitacao.cargo_proposto
        colaborador.salario = solicitacao.salario_proposto
        colaborador.save()
        
        solicitacao.status = 'efetivada'
        solicitacao.data_efetivacao = timezone.now().date()
        solicitacao.save()
        
        return solicitacao
    
    @staticmethod
    def _notificar_aprovadores(solicitacao):
        """Notifica aprovadores sobre nova solicitação"""
        pass
    
    @staticmethod
    def _notificar_aprovacao(solicitacao):
        """Notifica sobre aprovação"""
        pass


class ReconhecimentoService:
    """Serviço para gestão de reconhecimentos"""
    
    @staticmethod
    def criar_reconhecimento(colaborador, reconhecido_por, dados):
        """Cria novo reconhecimento"""
        from .models import Reconhecimento
        
        reconhecimento = Reconhecimento.objects.create(
            colaborador=colaborador,
            reconhecido_por=reconhecido_por,
            data_reconhecimento=timezone.now(),
            **dados
        )
        
        # Cria notificação para o colaborador
        ReconhecimentoService._notificar_reconhecimento(reconhecimento)
        
        return reconhecimento
    
    @staticmethod
    def curtir_reconhecimento(reconhecimento, usuario):
        """Registra curtida em reconhecimento"""
        # Implementação simplificada
        reconhecimento.curtidas += 1
        reconhecimento.save()
        return reconhecimento
    
    @staticmethod
    def ranking_reconhecimentos(periodo_dias=30):
        """Gera ranking de colaboradores mais reconhecidos"""
        from .models import Reconhecimento
        
        data_inicio = timezone.now() - timedelta(days=periodo_dias)
        
        return list(
            Reconhecimento.objects.filter(
                data_reconhecimento__gte=data_inicio,
                is_active=True
            ).values(
                'colaborador__id',
                'colaborador__nome'
            ).annotate(
                total=Count('id'),
                pontos=Sum('pontos')
            ).order_by('-total')[:10]
        )
    
    @staticmethod
    def _notificar_reconhecimento(reconhecimento):
        """Notifica colaborador sobre reconhecimento"""
        from .models import NotificacaoColaborador
        
        NotificacaoColaborador.objects.create(
            colaborador=reconhecimento.colaborador,
            tipo='reconhecimento',
            titulo='Você foi reconhecido!',
            mensagem=f'{reconhecimento.reconhecido_por.get_full_name()} te reconheceu: {reconhecimento.titulo}',
            importante=True
        )


class RetencaoService:
    """Serviço para análise de retenção e rotatividade"""
    
    @staticmethod
    def analisar_risco_rotatividade(colaborador):
        """Analisa risco de rotatividade do colaborador"""
        from .models import AlertaRotatividade
        
        fatores_risco = []
        probabilidade = 0
        
        # Tempo de empresa sem promoção
        # Implementação futura: verificar histórico
        
        # Resultado de pesquisas de clima
        # Implementação futura
        
        # eNPS individual
        # Implementação futura
        
        # Ausências frequentes
        # Implementação futura
        
        nivel_risco = 'baixo'
        if probabilidade > 70:
            nivel_risco = 'critico'
        elif probabilidade > 50:
            nivel_risco = 'alto'
        elif probabilidade > 30:
            nivel_risco = 'medio'
        
        alerta, created = AlertaRotatividade.objects.update_or_create(
            colaborador=colaborador,
            status='ativo',
            defaults={
                'nivel_risco': nivel_risco,
                'probabilidade_saida': probabilidade,
                'fatores_risco': fatores_risco
            }
        )
        
        return alerta
    
    @staticmethod
    def radar_rotatividade(departamento=None):
        """Gera radar de rotatividade"""
        from .models import AlertaRotatividade
        
        filtros = {'status': 'ativo'}
        if departamento:
            filtros['colaborador__departamento'] = departamento
        
        alertas = AlertaRotatividade.objects.filter(**filtros)
        
        return {
            'total_alertas': alertas.count(),
            'criticos': alertas.filter(nivel_risco='critico').count(),
            'altos': alertas.filter(nivel_risco='alto').count(),
            'medios': alertas.filter(nivel_risco='medio').count(),
            'baixos': alertas.filter(nivel_risco='baixo').count(),
            'colaboradores_risco': list(
                alertas.filter(
                    nivel_risco__in=['critico', 'alto']
                ).values(
                    'colaborador__id',
                    'colaborador__nome',
                    'nivel_risco',
                    'probabilidade_saida'
                )[:20]
            )
        }
    
    @staticmethod
    def calcular_turnover(periodo_inicio, periodo_fim, departamento=None):
        """Calcula taxa de turnover"""
        from apps.departamento_pessoal.models import Colaborador
        
        filtros_ativos = {'status': 'ativo'}
        filtros_desligados = {
            'status': 'desligado',
            'data_demissao__gte': periodo_inicio,
            'data_demissao__lte': periodo_fim
        }
        
        if departamento:
            filtros_ativos['departamento'] = departamento
            filtros_desligados['departamento'] = departamento
        
        ativos_inicio = Colaborador.objects.filter(
            data_admissao__lt=periodo_inicio,
            **{k: v for k, v in filtros_ativos.items() if k != 'status'}
        ).count()
        
        ativos_fim = Colaborador.objects.filter(**filtros_ativos).count()
        
        desligados = Colaborador.objects.filter(**filtros_desligados).count()
        
        media_colaboradores = (ativos_inicio + ativos_fim) / 2
        
        if media_colaboradores == 0:
            return 0
        
        turnover = (desligados / media_colaboradores) * 100
        
        return round(turnover, 2)


class NotificacaoService:
    """Serviço para gestão de notificações"""
    
    @staticmethod
    def criar_notificacao(colaborador, tipo, titulo, mensagem, **kwargs):
        """Cria nova notificação"""
        from .models import NotificacaoColaborador
        
        return NotificacaoColaborador.objects.create(
            colaborador=colaborador,
            tipo=tipo,
            titulo=titulo,
            mensagem=mensagem,
            **kwargs
        )
    
    @staticmethod
    def marcar_como_lida(notificacao):
        """Marca notificação como lida"""
        notificacao.lida = True
        notificacao.data_leitura = timezone.now()
        notificacao.save()
        return notificacao
    
    @staticmethod
    def obter_nao_lidas(colaborador):
        """Obtém notificações não lidas"""
        from .models import NotificacaoColaborador
        
        return NotificacaoColaborador.objects.filter(
            colaborador=colaborador,
            lida=False,
            is_active=True
        ).order_by('-created_at')
    
    @staticmethod
    def limpar_expiradas():
        """Remove notificações expiradas"""
        from .models import NotificacaoColaborador
        
        expiradas = NotificacaoColaborador.objects.filter(
            expira_em__lt=timezone.now()
        )
        
        count = expiradas.count()
        expiradas.delete()
        
        return count
