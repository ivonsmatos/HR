"""
SyncRH - Recrutamento e Seleção - Views
=======================================
"""

from rest_framework import viewsets, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Count, Q
from django.utils import timezone

from .models import (
    Vaga, Candidato, CandidaturaVaga, Entrevista,
    PerfilCargo, PerfilComportamental, MatchPerfil
)


class VagaViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciamento de vagas"""
    queryset = Vaga.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        status_param = self.request.query_params.get('status')
        departamento = self.request.query_params.get('departamento')
        
        if status_param:
            queryset = queryset.filter(status=status_param)
        if departamento:
            queryset = queryset.filter(departamento_id=departamento)
        
        return queryset.annotate(
            total_candidatos=Count('candidaturas')
        )
    
    @action(detail=True, methods=['get'])
    def candidatos(self, request, pk=None):
        """Lista candidatos da vaga"""
        vaga = self.get_object()
        candidaturas = CandidaturaVaga.objects.filter(vaga=vaga)
        return Response([{
            'id': c.candidato.id,
            'nome': c.candidato.nome_completo,
            'status': c.status,
            'match': c.match_score
        } for c in candidaturas])


class CandidatoViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciamento de candidatos"""
    queryset = Candidato.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticated]


class CandidaturaViewSet(viewsets.ModelViewSet):
    """ViewSet para candidaturas"""
    queryset = CandidaturaVaga.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def avancar_etapa(self, request, pk=None):
        """Avança candidatura para próxima etapa"""
        candidatura = self.get_object()
        # Lógica de avanço
        return Response({'status': 'avancado'})


class EntrevistaViewSet(viewsets.ModelViewSet):
    """ViewSet para entrevistas"""
    queryset = Entrevista.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class PerfilCargoViewSet(viewsets.ModelViewSet):
    """ViewSet para perfis de cargo"""
    queryset = PerfilCargo.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticated]


class DashboardRecrutamentoView(APIView):
    """Dashboard de Recrutamento"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        return Response({
            'vagas_abertas': Vaga.objects.filter(status='aberta').count(),
            'candidatos_ativos': Candidato.objects.filter(is_active=True).count(),
            'entrevistas_pendentes': Entrevista.objects.filter(status='agendada').count(),
        })


class PaginaCarreirasView(APIView):
    """API pública para página de carreiras"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        vagas = Vaga.objects.filter(
            status='aberta',
            publicar_site=True
        ).values('id', 'titulo', 'departamento__nome', 'cidade', 'tipo_contrato')
        
        return Response(list(vagas))
