"""
SyncRH - Gestão Comportamental - URLs
=====================================
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'gestao_comportamental'

router = DefaultRouter()
router.register(r'questionarios', views.QuestionarioProfilerViewSet, basename='questionario')
router.register(r'aplicacoes', views.AplicacaoProfilerViewSet, basename='aplicacao')
router.register(r'perfis', views.PerfilDISCViewSet, basename='perfil')
router.register(r'perfis-ideais', views.PerfilIdealCargoViewSet, basename='perfil-ideal')
router.register(r'matches', views.MatchComportamentalViewSet, basename='match')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/dashboard/', views.DashboardComportamentalView.as_view(), name='dashboard'),
    path('api/meu-perfil/', views.MeuPerfilView.as_view(), name='meu-perfil'),
    path('api/comparacao-time/', views.ComparacaoTimeView.as_view(), name='comparacao-time'),
]
