"""
SyncRH - Departamento Pessoal - URLs
====================================

Definição das rotas do módulo Departamento Pessoal.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'departamento_pessoal'

router = DefaultRouter()
router.register(r'colaboradores', views.ColaboradorViewSet, basename='colaborador')
router.register(r'departamentos', views.DepartamentoViewSet, basename='departamento')
router.register(r'cargos', views.CargoViewSet, basename='cargo')
router.register(r'registros-ponto', views.RegistroPontoViewSet, basename='registro-ponto')
router.register(r'folhas-pagamento', views.FolhaPagamentoViewSet, basename='folha-pagamento')
router.register(r'ferias', views.SolicitacaoFeriasViewSet, basename='ferias')
router.register(r'documentos', views.DocumentoGEDViewSet, basename='documento')

urlpatterns = [
    path('api/', include(router.urls)),
    
    # Endpoints customizados
    path('api/ponto/registrar/', views.RegistrarPontoView.as_view(), name='registrar-ponto'),
    path('api/ponto/meu-espelho/', views.MeuEspelhoPontoView.as_view(), name='meu-espelho-ponto'),
    path('api/dashboard/', views.DashboardDPView.as_view(), name='dashboard'),
]
