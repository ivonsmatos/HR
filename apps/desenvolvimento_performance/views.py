"""
SyncRH - Desenvolvimento e Performance - Views
==============================================
"""

from rest_framework import viewsets, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Avg, Count
from django.utils import timezone

from .models import (
    CicloAvaliacao, AvaliacaoDesempenho, SyncBox,
    PDI, MetaPDI, Curso, MatriculaCurso, ProgressoAula
)


class CicloAvaliacaoViewSet(viewsets.ModelViewSet):
    """ViewSet para ciclos de avaliação"""
    queryset = CicloAvaliacao.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticated]


class AvaliacaoDesempenhoViewSet(viewsets.ModelViewSet):
    """ViewSet para avaliações de desempenho"""
    queryset = AvaliacaoDesempenho.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        if not user.is_staff:
            # Mostra apenas avaliações onde o usuário é avaliador ou avaliado
            try:
                colaborador = user.colaborador
                queryset = queryset.filter(
                    models.Q(avaliado=colaborador) |
                    models.Q(avaliador=user)
                )
            except:
                queryset = queryset.none()
        
        return queryset


class PDIViewSet(viewsets.ModelViewSet):
    """ViewSet para PDIs"""
    queryset = PDI.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def adicionar_meta(self, request, pk=None):
        """Adiciona meta ao PDI"""
        pdi = self.get_object()
        MetaPDI.objects.create(
            pdi=pdi,
            titulo=request.data.get('titulo'),
            descricao=request.data.get('descricao'),
            prazo=request.data.get('prazo')
        )
        return Response({'status': 'meta_adicionada'})


class SyncBoxViewSet(viewsets.ModelViewSet):
    """ViewSet para SyncBox (9Box)"""
    queryset = SyncBox.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def matriz(self, request):
        """Retorna matriz 9Box"""
        ciclo = request.query_params.get('ciclo')
        
        qs = SyncBox.objects.all()
        if ciclo:
            qs = qs.filter(ciclo_id=ciclo)
        
        # Agrupa por quadrante
        matriz = qs.values('quadrante').annotate(total=Count('id'))
        
        return Response({
            'matriz': list(matriz),
            'total': qs.count()
        })


class CursoViewSet(viewsets.ModelViewSet):
    """ViewSet para cursos LMS"""
    queryset = Curso.objects.filter(is_active=True, publicado=True)
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def matricular(self, request, pk=None):
        """Matricula usuário no curso"""
        curso = self.get_object()
        try:
            colaborador = request.user.colaborador
            matricula, created = MatriculaCurso.objects.get_or_create(
                curso=curso,
                colaborador=colaborador
            )
            return Response({
                'matriculado': True,
                'nova_matricula': created
            })
        except:
            return Response(
                {'error': 'Usuário não possui cadastro de colaborador'},
                status=status.HTTP_400_BAD_REQUEST
            )


class MatriculaCursoViewSet(viewsets.ModelViewSet):
    """ViewSet para matrículas em cursos"""
    queryset = MatriculaCurso.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class DashboardPerformanceView(APIView):
    """Dashboard de Performance"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        return Response({
            'avaliacoes_pendentes': AvaliacaoDesempenho.objects.filter(
                status='em_andamento'
            ).count(),
            'pdis_ativos': PDI.objects.filter(status='ativo').count(),
            'cursos_disponiveis': Curso.objects.filter(
                is_active=True,
                publicado=True
            ).count(),
            'media_conclusao_cursos': MatriculaCurso.objects.filter(
                status='concluido'
            ).aggregate(media=Avg('progresso'))['media'] or 0
        })


class MeuPDIView(APIView):
    """PDI do colaborador logado"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            colaborador = request.user.colaborador
            pdis = PDI.objects.filter(
                colaborador=colaborador,
                is_active=True
            ).prefetch_related('metas')
            
            return Response([{
                'id': pdi.id,
                'titulo': pdi.titulo,
                'status': pdi.status,
                'progresso': pdi.progresso,
                'metas': [{
                    'titulo': m.titulo,
                    'status': m.status,
                    'prazo': m.prazo
                } for m in pdi.metas.all()]
            } for pdi in pdis])
        except:
            return Response([])


class MeusCursosView(APIView):
    """Cursos do colaborador logado"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            colaborador = request.user.colaborador
            matriculas = MatriculaCurso.objects.filter(
                colaborador=colaborador
            ).select_related('curso')
            
            return Response([{
                'curso': m.curso.titulo,
                'progresso': m.progresso,
                'status': m.status,
                'data_matricula': m.data_matricula
            } for m in matriculas])
        except:
            return Response([])
