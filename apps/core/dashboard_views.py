"""
Dashboard Views - Frontend do Sistema SyncRH
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def home(request):
    """Dashboard principal"""
    context = {
        'stats': {
            'total_employees': 247,
            'total_departments': 12,
            'active_projects': 23,
            'open_positions': 8,
        }
    }
    return render(request, 'dashboard/home.html', context)


@login_required
def employees(request):
    """Lista de funcionários"""
    return render(request, 'dashboard/employees.html')


@login_required
def departments(request):
    """Departamentos"""
    return render(request, 'dashboard/generic_module.html', {
        'page_title': 'Departamentos',
        'page_subtitle': 'Estrutura organizacional da empresa',
        'page_icon': 'fas fa-building',
        'stat1_value': '12', 'stat1_label': 'Departamentos',
        'stat2_value': '247', 'stat2_label': 'Funcionários',
        'stat3_value': '15', 'stat3_label': 'Gestores',
    })


@login_required
def recruitment(request):
    """Recrutamento e seleção"""
    return render(request, 'dashboard/generic_module.html', {
        'page_title': 'Recrutamento',
        'page_subtitle': 'Gestão de vagas e candidatos',
        'page_icon': 'fas fa-user-plus',
        'stat1_value': '8', 'stat1_label': 'Vagas Abertas',
        'stat2_value': '34', 'stat2_label': 'Candidatos',
        'stat3_value': '12', 'stat3_label': 'Entrevistas',
    })


@login_required
def payroll(request):
    """Folha de pagamento"""
    return render(request, 'dashboard/generic_module.html', {
        'page_title': 'Folha de Pagamento',
        'page_subtitle': 'Gestão de salários e pagamentos',
        'page_icon': 'fas fa-money-bill-wave',
        'stat1_value': 'R$ 1.2M', 'stat1_label': 'Folha Mensal',
        'stat2_value': '247', 'stat2_label': 'Funcionários',
        'stat3_value': '15', 'stat3_label': 'Pendências',
    })


@login_required
def benefits(request):
    """Benefícios"""
    return render(request, 'dashboard/generic_module.html', {
        'page_title': 'Benefícios',
        'page_subtitle': 'Gestão de benefícios dos colaboradores',
        'page_icon': 'fas fa-gift',
        'stat1_value': '5', 'stat1_label': 'Tipos',
        'stat2_value': '247', 'stat2_label': 'Elegíveis',
        'stat3_value': 'R$ 234K', 'stat3_label': 'Valor Mensal',
    })


@login_required
def vacation(request):
    """Férias"""
    return render(request, 'dashboard/generic_module.html', {
        'page_title': 'Férias',
        'page_subtitle': 'Controle de férias e licenças',
        'page_icon': 'fas fa-umbrella-beach',
        'stat1_value': '12', 'stat1_label': 'Em Férias',
        'stat2_value': '45', 'stat2_label': 'Vencendo',
        'stat3_value': '8', 'stat3_label': 'Solicitações',
    })


@login_required
def timesheet(request):
    """Controle de ponto"""
    return render(request, 'dashboard/generic_module.html', {
        'page_title': 'Controle de Ponto',
        'page_subtitle': 'Registro de jornada de trabalho',
        'page_icon': 'fas fa-clock',
        'stat1_value': '232', 'stat1_label': 'Presentes Hoje',
        'stat2_value': '15', 'stat2_label': 'Ausentes',
        'stat3_value': '23', 'stat3_label': 'Horas Extras',
    })


@login_required
def performance(request):
    """Avaliação de performance"""
    return render(request, 'dashboard/generic_module.html', {
        'page_title': 'Avaliação de Performance',
        'page_subtitle': 'Avaliações e feedbacks de colaboradores',
        'page_icon': 'fas fa-chart-line',
        'stat1_value': '156', 'stat1_label': 'Avaliações',
        'stat2_value': '4.2', 'stat2_label': 'Média Geral',
        'stat3_value': '45', 'stat3_label': 'Pendentes',
    })


@login_required
def goals(request):
    """Metas e OKRs"""
    return render(request, 'dashboard/generic_module.html', {
        'page_title': 'Metas & OKRs',
        'page_subtitle': 'Gestão de objetivos e resultados-chave',
        'page_icon': 'fas fa-bullseye',
        'stat1_value': '48', 'stat1_label': 'OKRs Ativos',
        'stat2_value': '72%', 'stat2_label': 'Conclusão',
        'stat3_value': '12', 'stat3_label': 'Atrasados',
    })


@login_required
def training(request):
    """Treinamentos"""
    return render(request, 'dashboard/generic_module.html', {
        'page_title': 'Treinamentos',
        'page_subtitle': 'Capacitação e desenvolvimento',
        'page_icon': 'fas fa-graduation-cap',
        'stat1_value': '23', 'stat1_label': 'Cursos Ativos',
        'stat2_value': '1.2K', 'stat2_label': 'Inscrições',
        'stat3_value': '89%', 'stat3_label': 'Conclusão',
    })


@login_required
def projects(request):
    """Projetos"""
    return render(request, 'dashboard/projects.html')


@login_required
def tasks(request):
    """Tarefas"""
    return render(request, 'dashboard/generic_module.html', {
        'page_title': 'Tarefas',
        'page_subtitle': 'Gestão de tarefas e atividades',
        'page_icon': 'fas fa-tasks',
        'stat1_value': '156', 'stat1_label': 'Total',
        'stat2_value': '89', 'stat2_label': 'Concluídas',
        'stat3_value': '23', 'stat3_label': 'Atrasadas',
    })


@login_required
def clients(request):
    """Clientes"""
    return render(request, 'dashboard/generic_module.html', {
        'page_title': 'Clientes',
        'page_subtitle': 'Gestão de relacionamento com clientes',
        'page_icon': 'fas fa-handshake',
        'stat1_value': '89', 'stat1_label': 'Clientes',
        'stat2_value': '34', 'stat2_label': 'Leads',
        'stat3_value': 'R$ 2.4M', 'stat3_label': 'Receita',
    })


@login_required
def invoices(request):
    """Faturas"""
    return render(request, 'dashboard/generic_module.html', {
        'page_title': 'Faturas',
        'page_subtitle': 'Gestão financeira e faturamento',
        'page_icon': 'fas fa-file-invoice-dollar',
        'stat1_value': '156', 'stat1_label': 'Faturas',
        'stat2_value': 'R$ 890K', 'stat2_label': 'A Receber',
        'stat3_value': '23', 'stat3_label': 'Vencidas',
    })


@login_required
def settings(request):
    """Configurações"""
    return render(request, 'dashboard/generic_module.html', {
        'page_title': 'Configurações',
        'page_subtitle': 'Configurações do sistema',
        'page_icon': 'fas fa-cog',
        'page_description': 'Gerencie as configurações gerais do sistema, integrações e preferências.',
        'stat1_value': '5', 'stat1_label': 'Integrações',
        'stat2_value': '12', 'stat2_label': 'Usuários',
        'stat3_value': '3', 'stat3_label': 'Empresas',
    })


@login_required
def reports(request):
    """Relatórios"""
    return render(request, 'dashboard/generic_module.html', {
        'page_title': 'Relatórios',
        'page_subtitle': 'Relatórios e análises do sistema',
        'page_icon': 'fas fa-chart-bar',
        'page_description': 'Acesse relatórios detalhados de RH, financeiro, projetos e mais.',
        'stat1_value': '45', 'stat1_label': 'Relatórios',
        'stat2_value': '12', 'stat2_label': 'Dashboards',
        'stat3_value': '89', 'stat3_label': 'Exportações',
    })
