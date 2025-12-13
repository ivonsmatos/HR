"""
SyncRH - Gestão Comportamental - Views
======================================
"""

from rest_framework import viewsets, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Avg, Count
from django.utils import timezone

from .models import (
    QuestionarioProfiler, AplicacaoProfiler, PerfilDISC,
    PerfilIdealCargo, MatchComportamental, ComparacaoTime
)


class QuestionarioProfilerViewSet(viewsets.ModelViewSet):
    """ViewSet para questionários profiler"""
    queryset = QuestionarioProfiler.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(publicado=True)
        return queryset


class AplicacaoProfilerViewSet(viewsets.ModelViewSet):
    """ViewSet para aplicações do profiler"""
    queryset = AplicacaoProfiler.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def iniciar(self, request, pk=None):
        """Inicia aplicação do questionário"""
        aplicacao = self.get_object()
        aplicacao.status = 'em_andamento'
        aplicacao.data_inicio = timezone.now()
        aplicacao.save()
        return Response({'iniciado': True})
    
    @action(detail=True, methods=['post'])
    def finalizar(self, request, pk=None):
        """Finaliza aplicação e calcula perfil"""
        aplicacao = self.get_object()
        aplicacao.status = 'concluido'
        aplicacao.data_conclusao = timezone.now()
        aplicacao.save()
        
        # Calcula perfil DISC
        perfil = self._calcular_perfil(aplicacao)
        
        return Response({
            'finalizado': True,
            'perfil': {
                'D': perfil.dominancia,
                'I': perfil.influencia,
                'S': perfil.estabilidade,
                'C': perfil.conformidade,
                'principal': perfil.perfil_principal
            }
        })
    
    def _calcular_perfil(self, aplicacao):
        """Calcula perfil DISC baseado nas respostas"""
        # Lógica simplificada - em produção seria mais complexa
        perfil = PerfilDISC.objects.create(
            aplicacao=aplicacao,
            dominancia=50,
            influencia=50,
            estabilidade=50,
            conformidade=50,
            tipo_perfil='natural'
        )
        perfil.calcular_perfil_principal()
        perfil.save()
        return perfil


class PerfilDISCViewSet(viewsets.ModelViewSet):
    """ViewSet para perfis DISC"""
    queryset = PerfilDISC.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class PerfilIdealCargoViewSet(viewsets.ModelViewSet):
    """ViewSet para perfis ideais de cargo"""
    queryset = PerfilIdealCargo.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticated]


class MatchComportamentalViewSet(viewsets.ModelViewSet):
    """ViewSet para matches comportamentais"""
    queryset = MatchComportamental.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def calcular(self, request):
        """Calcula match entre perfil e cargo"""
        perfil_id = request.data.get('perfil_id')
        cargo_id = request.data.get('cargo_id')
        
        try:
            perfil = PerfilDISC.objects.get(id=perfil_id)
            perfil_ideal = PerfilIdealCargo.objects.get(cargo_id=cargo_id)
            
            match, created = MatchComportamental.objects.get_or_create(
                perfil_disc=perfil,
                perfil_ideal=perfil_ideal
            )
            match.calcular_match()
            match.save()
            
            return Response({
                'match_geral': float(match.match_geral),
                'classificacao': match.classificacao,
                'detalhes': {
                    'D': float(match.match_dominancia),
                    'I': float(match.match_influencia),
                    'S': float(match.match_estabilidade),
                    'C': float(match.match_conformidade)
                }
            })
        except Exception as e:
            return Response({'error': str(e)}, status=400)


class DashboardComportamentalView(APIView):
    """Dashboard Comportamental"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Distribuição de perfis
        distribuicao = PerfilDISC.objects.values(
            'perfil_principal'
        ).annotate(total=Count('id'))
        
        # Média de match
        media_match = MatchComportamental.objects.aggregate(
            media=Avg('match_geral')
        )['media'] or 0
        
        # Aplicações pendentes
        pendentes = AplicacaoProfiler.objects.filter(
            status='pendente'
        ).count()
        
        return Response({
            'distribuicao_perfis': list(distribuicao),
            'media_match': float(media_match),
            'aplicacoes_pendentes': pendentes,
            'total_perfis': PerfilDISC.objects.count()
        })


class MeuPerfilView(APIView):
    """Perfil DISC do colaborador logado"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            colaborador = request.user.colaborador
            aplicacao = AplicacaoProfiler.objects.filter(
                colaborador=colaborador,
                status='concluido'
            ).order_by('-data_conclusao').first()
            
            if not aplicacao:
                return Response({'perfil': None})
            
            perfil = aplicacao.perfil_disc
            
            return Response({
                'perfil': {
                    'D': perfil.dominancia,
                    'I': perfil.influencia,
                    'S': perfil.estabilidade,
                    'C': perfil.conformidade,
                    'principal': perfil.perfil_principal,
                    'padrao': perfil.padrao,
                    'pontos_fortes': perfil.pontos_fortes,
                    'areas_desenvolvimento': perfil.areas_desenvolvimento
                },
                'data_avaliacao': aplicacao.data_conclusao
            })
        except:
            return Response({'perfil': None})


class ComparacaoTimeView(APIView):
    """Comparação de perfis de um time"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        departamento_id = request.query_params.get('departamento')
        
        if not departamento_id:
            return Response({'error': 'Departamento não informado'}, status=400)
        
        # Busca comparação existente ou cria análise
        comparacao = ComparacaoTime.objects.filter(
            departamento_id=departamento_id
        ).first()
        
        if comparacao:
            return Response({
                'nome': comparacao.nome,
                'mapa_time': comparacao.mapa_time,
                'gaps': comparacao.gaps_identificados,
                'pontos_fortes': comparacao.pontos_fortes_time,
                'pontos_atencao': comparacao.pontos_atencao_time
            })
        
        return Response({'comparacao': None})
    
    def post(self, request):
        """Gera nova comparação de time"""
        departamento_id = request.data.get('departamento')
        nome = request.data.get('nome', f'Análise {timezone.now().date()}')
        
        comparacao = ComparacaoTime.objects.create(
            nome=nome,
            departamento_id=departamento_id,
            criado_por=request.user
        )
        
        # Lógica de análise seria implementada aqui
        
        return Response({
            'id': comparacao.id,
            'criado': True
        })
