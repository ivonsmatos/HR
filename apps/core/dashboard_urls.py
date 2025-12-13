"""
Dashboard URLs - Rotas do Frontend SyncRH
"""
from django.urls import path
from . import dashboard_views as views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('employees/', views.employees, name='employees'),
    path('departments/', views.departments, name='departments'),
    path('recruitment/', views.recruitment, name='recruitment'),
    path('payroll/', views.payroll, name='payroll'),
    path('benefits/', views.benefits, name='benefits'),
    path('vacation/', views.vacation, name='vacation'),
    path('timesheet/', views.timesheet, name='timesheet'),
    path('performance/', views.performance, name='performance'),
    path('goals/', views.goals, name='goals'),
    path('training/', views.training, name='training'),
    path('projects/', views.projects, name='projects'),
    path('tasks/', views.tasks, name='tasks'),
    path('clients/', views.clients, name='clients'),
    path('invoices/', views.invoices, name='invoices'),
    path('settings/', views.settings, name='settings'),
    path('reports/', views.reports, name='reports'),
]
