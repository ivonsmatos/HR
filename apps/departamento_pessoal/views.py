"""
SyncRH - Departamento Pessoal - Views
=====================================

Views e ViewSets do módulo Departamento Pessoal.
"""

from rest_framework import viewsets, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from django.db.models import Count, Sum, Q
from datetime import date, timedelta

from .models import (
    Colaborador, Departamento, Cargo, RegistroPonto,
    FolhaPagamento, SolicitacaoFerias, DocumentoGED
)
from .serializers import (
    ColaboradorSerializer, ColaboradorListSerializer,
    DepartamentoSerializer, CargoSerializer,
    RegistroPontoSerializer, FolhaPagamentoSerializer,
    SolicitacaoFeriasSerializer, DocumentoGEDSerializer
)
from .services import PontoService, FeriasService


class ColaboradorViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de colaboradores.
    
    Endpoints:
    - GET /api/colaboradores/ - Lista colaboradores
    - POST /api/colaboradores/ - Cria colaborador
    - GET /api/colaboradores/{id}/ - Detalhe do colaborador
    - PUT /api/colaboradores/{id}/ - Atualiza colaborador
    - DELETE /api/colaboradores/{id}/ - Remove colaborador
    """
    queryset = Colaborador.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ColaboradorListSerializer
        return ColaboradorSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros
        departamento = self.request.query_params.get('departamento')
        cargo = self.request.query_params.get('cargo')
        status_param = self.request.query_params.get('status')
        
        if departamento:
            queryset = queryset.filter(departamento_id=departamento)
        if cargo:
            queryset = queryset.filter(cargo_id=cargo)
        if status_param == 'ativos':
            queryset = queryset.filter(data_demissao__isnull=True)
        elif status_param == 'desligados':
            queryset = queryset.filter(data_demissao__isnull=False)
        
        return queryset.select_related('cargo', 'departamento', 'gestor')
    
    @action(detail=True, methods=['get'])
    def subordinados(self, request, pk=None):
        """Lista subordinados do colaborador"""
        colaborador = self.get_object()
        subordinados = Colaborador.objects.filter(gestor=colaborador, is_active=True)
        serializer = ColaboradorListSerializer(subordinados, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def historico(self, request, pk=None):
        """Histórico do colaborador"""
        colaborador = self.get_object()
        return Response({
            'tempo_empresa': colaborador.tempo_empresa,
            'ferias': colaborador.ferias_historico,
            'avaliacoes': colaborador.avaliacoes_count,
        })


class DepartamentoViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciamento de departamentos"""
    queryset = Departamento.objects.filter(is_active=True)
    serializer_class = DepartamentoSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return super().get_queryset().annotate(
            total_colaboradores=Count('colaboradores', filter=Q(colaboradores__is_active=True))
        )


class CargoViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciamento de cargos"""
    queryset = Cargo.objects.filter(is_active=True)
    serializer_class = CargoSerializer
    permission_classes = [permissions.IsAuthenticated]


class RegistroPontoViewSet(viewsets.ModelViewSet):
    """ViewSet para registros de ponto"""
    queryset = RegistroPonto.objects.all()
    serializer_class = RegistroPontoSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros
        colaborador = self.request.query_params.get('colaborador')
        data_inicio = self.request.query_params.get('data_inicio')
        data_fim = self.request.query_params.get('data_fim')
        
        if colaborador:
            queryset = queryset.filter(colaborador_id=colaborador)
        if data_inicio:
            queryset = queryset.filter(data__gte=data_inicio)
        if data_fim:
            queryset = queryset.filter(data__lte=data_fim)
        
        return queryset.select_related('colaborador')


class RegistrarPontoView(APIView):
    """
    Endpoint para registrar ponto do colaborador.
    
    POST /api/ponto/registrar/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            colaborador = request.user.colaborador
        except Colaborador.DoesNotExist:
            return Response(
                {'error': 'Usuário não possui cadastro de colaborador'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = PontoService()
        resultado = service.registrar_ponto(
            colaborador=colaborador,
            origem=request.data.get('origem', 'web'),
            localizacao=request.data.get('localizacao'),
            observacao=request.data.get('observacao', '')
        )
        
        return Response(resultado, status=status.HTTP_201_CREATED)


class MeuEspelhoPontoView(APIView):
    """
    Endpoint para visualizar espelho de ponto do colaborador logado.
    
    GET /api/ponto/meu-espelho/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            colaborador = request.user.colaborador
        except Colaborador.DoesNotExist:
            return Response(
                {'error': 'Usuário não possui cadastro de colaborador'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        mes = request.query_params.get('mes', timezone.now().month)
        ano = request.query_params.get('ano', timezone.now().year)
        
        service = PontoService()
        espelho = service.gerar_espelho(colaborador, int(mes), int(ano))
        
        return Response(espelho)


class FolhaPagamentoViewSet(viewsets.ModelViewSet):
    """ViewSet para folhas de pagamento"""
    queryset = FolhaPagamento.objects.all()
    serializer_class = FolhaPagamentoSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros
        colaborador = self.request.query_params.get('colaborador')
        mes = self.request.query_params.get('mes')
        ano = self.request.query_params.get('ano')
        
        if colaborador:
            queryset = queryset.filter(colaborador_id=colaborador)
        if mes:
            queryset = queryset.filter(mes=mes)
        if ano:
            queryset = queryset.filter(ano=ano)
        
        return queryset.select_related('colaborador')


class SolicitacaoFeriasViewSet(viewsets.ModelViewSet):
    """ViewSet para solicitações de férias"""
    queryset = SolicitacaoFerias.objects.all()
    serializer_class = SolicitacaoFeriasSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Se não for gestor/RH, mostra apenas as próprias férias
        if not self.request.user.is_staff:
            try:
                queryset = queryset.filter(colaborador=self.request.user.colaborador)
            except Colaborador.DoesNotExist:
                queryset = queryset.none()
        
        return queryset.select_related('colaborador', 'periodo_aquisitivo')
    
    @action(detail=True, methods=['post'])
    def aprovar(self, request, pk=None):
        """Aprova solicitação de férias"""
        solicitacao = self.get_object()
        service = FeriasService()
        resultado = service.aprovar(solicitacao, request.user)
        return Response(resultado)
    
    @action(detail=True, methods=['post'])
    def rejeitar(self, request, pk=None):
        """Rejeita solicitação de férias"""
        solicitacao = self.get_object()
        motivo = request.data.get('motivo', '')
        service = FeriasService()
        resultado = service.rejeitar(solicitacao, request.user, motivo)
        return Response(resultado)


class DocumentoGEDViewSet(viewsets.ModelViewSet):
    """ViewSet para documentos GED"""
    queryset = DocumentoGED.objects.filter(is_active=True)
    serializer_class = DocumentoGEDSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros
        colaborador = self.request.query_params.get('colaborador')
        categoria = self.request.query_params.get('categoria')
        
        if colaborador:
            queryset = queryset.filter(colaborador_id=colaborador)
        if categoria:
            queryset = queryset.filter(categoria_id=categoria)
        
        return queryset.select_related('colaborador', 'categoria')


class DashboardDPView(APIView):
    """
    Dashboard do Departamento Pessoal.
    
    GET /api/dashboard/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        hoje = date.today()
        
        # Estatísticas gerais
        total_colaboradores = Colaborador.objects.filter(
            is_active=True,
            data_demissao__isnull=True
        ).count()
        
        admissoes_mes = Colaborador.objects.filter(
            data_admissao__month=hoje.month,
            data_admissao__year=hoje.year
        ).count()
        
        demissoes_mes = Colaborador.objects.filter(
            data_demissao__month=hoje.month,
            data_demissao__year=hoje.year
        ).count()
        
        ferias_pendentes = SolicitacaoFerias.objects.filter(
            status='pendente'
        ).count()
        
        # Aniversariantes do mês
        aniversariantes = Colaborador.objects.filter(
            is_active=True,
            data_nascimento__month=hoje.month
        ).values('nome_completo', 'data_nascimento')[:10]
        
        return Response({
            'total_colaboradores': total_colaboradores,
            'admissoes_mes': admissoes_mes,
            'demissoes_mes': demissoes_mes,
            'ferias_pendentes': ferias_pendentes,
            'aniversariantes': list(aniversariantes),
            'data_atualizacao': timezone.now()
        })
