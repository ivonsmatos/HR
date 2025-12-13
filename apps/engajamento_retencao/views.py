"""
SyncRH - Engajamento e Retenção - Views
=======================================
"""

from rest_framework import viewsets, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Avg, Count
from django.utils import timezone

from .models import (
    PesquisaClima, PesquisaeNPS, RespostaeNPS,
    AnaliseRotatividade, TipoBeneficio, BeneficioColaborador,
    SolicitacaoPromocao, NotificacaoColaborador, Reconhecimento
)


class PesquisaClimaViewSet(viewsets.ModelViewSet):
    """ViewSet para pesquisas de clima"""
    queryset = PesquisaClima.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=True, methods=['get'])
    def resultados(self, request, pk=None):
        """Retorna resultados da pesquisa"""
        pesquisa = self.get_object()
        return Response({
            'titulo': pesquisa.titulo,
            'taxa_participacao': pesquisa.taxa_participacao,
            'score_geral': pesquisa.score_geral,
            'dimensoes': list(pesquisa.dimensoes.values('nome', 'score_medio'))
        })


class PesquisaeNPSViewSet(viewsets.ModelViewSet):
    """ViewSet para pesquisas eNPS"""
    queryset = PesquisaeNPS.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def responder(self, request, pk=None):
        """Registra resposta da pesquisa"""
        pesquisa = self.get_object()
        nota = request.data.get('nota')
        comentario = request.data.get('comentario', '')
        
        try:
            colaborador = request.user.colaborador
        except:
            colaborador = None
        
        resposta = RespostaeNPS.objects.create(
            pesquisa=pesquisa,
            colaborador=colaborador,
            nota=nota,
            comentarios=comentario
        )
        
        # Atualiza contadores
        pesquisa.total_respostas += 1
        if nota >= 9:
            pesquisa.promotores += 1
        elif nota >= 7:
            pesquisa.neutros += 1
        else:
            pesquisa.detratores += 1
        pesquisa.calcular_enps()
        
        return Response({'registrado': True})


class TipoBeneficioViewSet(viewsets.ModelViewSet):
    """ViewSet para tipos de benefícios"""
    queryset = TipoBeneficio.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticated]


class SolicitacaoPromocaoViewSet(viewsets.ModelViewSet):
    """ViewSet para solicitações de promoção"""
    queryset = SolicitacaoPromocao.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def aprovar(self, request, pk=None):
        """Aprova solicitação"""
        solicitacao = self.get_object()
        solicitacao.status = 'aprovado'
        solicitacao.save()
        return Response({'aprovado': True})


class ReconhecimentoViewSet(viewsets.ModelViewSet):
    """ViewSet para reconhecimentos"""
    queryset = Reconhecimento.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Apenas reconhecimentos públicos ou próprios
        try:
            colaborador = self.request.user.colaborador
            queryset = queryset.filter(
                models.Q(publico=True) |
                models.Q(de_colaborador=colaborador) |
                models.Q(para_colaborador=colaborador)
            )
        except:
            queryset = queryset.filter(publico=True)
        return queryset


class DashboardEngajamentoView(APIView):
    """Dashboard de Engajamento"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Última pesquisa de clima
        ultima_clima = PesquisaClima.objects.filter(
            status='analisada'
        ).order_by('-data_fim').first()
        
        # Último eNPS
        ultimo_enps = PesquisaeNPS.objects.filter(
            status='encerrada'
        ).order_by('-data_fim').first()
        
        # Riscos de rotatividade
        riscos_altos = AnaliseRotatividade.objects.filter(
            classificacao__in=['alto', 'critico']
        ).count()
        
        return Response({
            'clima': {
                'score': ultima_clima.score_geral if ultima_clima else None,
                'participacao': ultima_clima.taxa_participacao if ultima_clima else None
            },
            'enps': {
                'score': ultimo_enps.score_enps if ultimo_enps else None,
                'promotores': ultimo_enps.promotores if ultimo_enps else 0,
                'detratores': ultimo_enps.detratores if ultimo_enps else 0
            },
            'rotatividade': {
                'riscos_altos': riscos_altos
            }
        })


class RadarRotatividadeView(APIView):
    """Radar de Rotatividade"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        analises = AnaliseRotatividade.objects.select_related(
            'colaborador'
        ).order_by('-score_risco')[:20]
        
        return Response([{
            'colaborador': a.colaborador.nome_completo,
            'score': a.score_risco,
            'classificacao': a.classificacao,
            'fatores': a.fatores[:3],  # Top 3 fatores
            'tendencia': a.tendencia
        } for a in analises])


class MeusBeneficiosView(APIView):
    """Benefícios do colaborador logado"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            colaborador = request.user.colaborador
            beneficios = BeneficioColaborador.objects.filter(
                colaborador=colaborador,
                status='ativo'
            ).select_related('tipo_beneficio')
            
            return Response([{
                'beneficio': b.tipo_beneficio.nome,
                'categoria': b.tipo_beneficio.categoria,
                'valor': str(b.valor),
                'desconto': str(b.valor_desconto)
            } for b in beneficios])
        except:
            return Response([])


class NotificacoesView(APIView):
    """Notificações do colaborador"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            colaborador = request.user.colaborador
            notificacoes = NotificacaoColaborador.objects.filter(
                colaborador=colaborador,
                lida=False
            ).order_by('-created_at')[:10]
            
            return Response([{
                'id': n.id,
                'titulo': n.titulo,
                'mensagem': n.mensagem,
                'tipo': n.tipo,
                'data': n.created_at
            } for n in notificacoes])
        except:
            return Response([])
    
    def post(self, request):
        """Marca notificação como lida"""
        notificacao_id = request.data.get('id')
        try:
            notificacao = NotificacaoColaborador.objects.get(id=notificacao_id)
            notificacao.lida = True
            notificacao.data_leitura = timezone.now()
            notificacao.save()
            return Response({'lida': True})
        except:
            return Response({'error': 'Notificação não encontrada'}, status=404)
