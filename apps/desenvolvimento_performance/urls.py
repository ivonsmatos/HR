"""
SyncRH - Desenvolvimento e Performance - URLs
=============================================
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'desenvolvimento_performance'

router = DefaultRouter()
router.register(r'ciclos-avaliacao', views.CicloAvaliacaoViewSet, basename='ciclo-avaliacao')
router.register(r'avaliacoes', views.AvaliacaoDesempenhoViewSet, basename='avaliacao')
router.register(r'pdis', views.PDIViewSet, basename='pdi')
router.register(r'cursos', views.CursoViewSet, basename='curso')
router.register(r'matriculas', views.MatriculaCursoViewSet, basename='matricula')
router.register(r'syncbox', views.SyncBoxViewSet, basename='syncbox')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/dashboard/', views.DashboardPerformanceView.as_view(), name='dashboard'),
    path('api/meu-pdi/', views.MeuPDIView.as_view(), name='meu-pdi'),
    path('api/meus-cursos/', views.MeusCursosView.as_view(), name='meus-cursos'),
]
