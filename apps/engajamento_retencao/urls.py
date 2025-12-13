"""
SyncRH - Engajamento e Retenção - URLs
======================================
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'engajamento_retencao'

router = DefaultRouter()
router.register(r'pesquisas-clima', views.PesquisaClimaViewSet, basename='pesquisa-clima')
router.register(r'pesquisas-enps', views.PesquisaeNPSViewSet, basename='pesquisa-enps')
router.register(r'beneficios', views.TipoBeneficioViewSet, basename='beneficio')
router.register(r'promocoes', views.SolicitacaoPromocaoViewSet, basename='promocao')
router.register(r'reconhecimentos', views.ReconhecimentoViewSet, basename='reconhecimento')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/dashboard/', views.DashboardEngajamentoView.as_view(), name='dashboard'),
    path('api/radar-rotatividade/', views.RadarRotatividadeView.as_view(), name='radar-rotatividade'),
    path('api/meus-beneficios/', views.MeusBeneficiosView.as_view(), name='meus-beneficios'),
    path('api/notificacoes/', views.NotificacoesView.as_view(), name='notificacoes'),
]
