"""
SyncRH - Recrutamento e Seleção - URLs
======================================
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'recrutamento_selecao'

router = DefaultRouter()
router.register(r'vagas', views.VagaViewSet, basename='vaga')
router.register(r'candidatos', views.CandidatoViewSet, basename='candidato')
router.register(r'candidaturas', views.CandidaturaViewSet, basename='candidatura')
router.register(r'entrevistas', views.EntrevistaViewSet, basename='entrevista')
router.register(r'perfis-cargo', views.PerfilCargoViewSet, basename='perfil-cargo')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/dashboard/', views.DashboardRecrutamentoView.as_view(), name='dashboard'),
    path('api/carreiras/', views.PaginaCarreirasView.as_view(), name='carreiras'),
]
