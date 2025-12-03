#!/usr/bin/env python3
"""
Script to translate all Django models from English to Portuguese (BR)
"""

import os
import re

# Translation mapping
TRANSLATIONS = {
    # verbose_name translations
    '"Project"': '"Projeto"',
    '"Projects"': '"Projetos"',
    '"Project Member"': '"Membro do Projeto"',
    '"Project Members"': '"Membros do Projeto"',
    '"Task"': '"Tarefa"',
    '"Tasks"': '"Tarefas"',
    '"Task Comment"': '"Comentário na Tarefa"',
    '"Task Comments"': '"Comentários nas Tarefas"',
    '"Time Log"': '"Registro de Tempo"',
    '"Time Logs"': '"Registros de Tempo"',
    '"Contract"': '"Contrato"',
    '"Contracts"': '"Contratos"',
    '"Department"': '"Departamento"',
    '"Departments"': '"Departamentos"',
    '"Designation"': '"Cargo/Designação"',
    '"Designations"': '"Cargos/Designações"',
    '"Employee"': '"Funcionário"',
    '"Employees"': '"Funcionários"',
    '"Leave Type"': '"Tipo de Licença"',
    '"Leave Types"': '"Tipos de Licença"',
    '"Leave"': '"Licença/Férias"',
    '"Leaves"': '"Licenças/Férias"',
    '"Shift"': '"Turno"',
    '"Shifts"': '"Turnos"',
    '"Attendance"': '"Frequência"',
    '"Salary Structure"': '"Estrutura Salarial"',
    '"Salary Structures"': '"Estruturas Salariais"',
    '"Employee Salary"': '"Salário do Funcionário"',
    '"Employee Salaries"': '"Salários dos Funcionários"',
    '"Payslip"': '"Contracheque"',
    '"Payslips"': '"Contracheques"',
    '"Performance Goal"': '"Meta de Desempenho"',
    '"Performance Goals"': '"Metas de Desempenho"',
    '"Performance Review"': '"Avaliação de Desempenho"',
    '"Performance Reviews"': '"Avaliações de Desempenho"',
    '"Client"': '"Cliente"',
    '"Clients"': '"Clientes"',
    '"Lead"': '"Lead/Oportunidade"',
    '"Leads"': '"Leads/Oportunidades"',
    '"Product"': '"Produto"',
    '"Products"': '"Produtos"',
    '"Order"': '"Pedido"',
    '"Orders"': '"Pedidos"',
    '"Order Item"': '"Item do Pedido"',
    '"Order Items"': '"Itens do Pedido"',
    '"Ticket"': '"Ticket/Chamado"',
    '"Tickets"': '"Tickets/Chamados"',
    '"Ticket Reply"': '"Resposta do Ticket"',
    '"Ticket Replies"': '"Respostas do Ticket"',
    '"Asset"': '"Ativo/Bem"',
    '"Assets"': '"Ativos/Bens"',
    '"Event"': '"Evento"',
    '"Events"': '"Eventos"',
    '"Message"': '"Mensagem"',
    '"Messages"': '"Mensagens"',
    '"Notice"': '"Aviso"',
    '"Notices"': '"Avisos"',
    '"IP Blocklist"': '"Lista Bloqueada de IP"',
    '"IP Blocklists"': '"Listas Bloqueadas de IP"',
    '"Two Factor Auth"': '"Autenticação de Dois Fatores"',
    '"Two Factor Auths"': '"Autenticações de Dois Fatores"',
    '"User Session"': '"Sessão do Usuário"',
    '"User Sessions"': '"Sessões do Usuário"',
    '"Security Event"': '"Evento de Segurança"',
    '"Security Events"': '"Eventos de Segurança"',
    '"Audit Config"': '"Configuração de Auditoria"',
    '"Audit Configs"': '"Configurações de Auditoria"',
    '"Subscription Plan"': '"Plano de Assinatura"',
    '"Subscription Plans"': '"Planos de Assinatura"',
    '"Subscription"': '"Assinatura"',
    '"Subscriptions"': '"Assinaturas"',
    '"Billing Invoice"': '"Fatura de Cobrança"',
    '"Billing Invoices"': '"Faturas de Cobrança"',
    '"Coupon"': '"Cupom"',
    '"Coupons"': '"Cupons"',
    '"Job"': '"Vaga/Emprego"',
    '"Jobs"': '"Vagas/Empregos"',
    '"Job Application"': '"Candidatura/Solicitação de Emprego"',
    '"Job Applications"': '"Candidaturas/Solicitações de Emprego"',
    '"Interview Schedule"': '"Agendamento de Entrevista"',
    '"Interview Schedules"': '"Agendamentos de Entrevista"',
    '"Offer Letter"': '"Carta de Oferta"',
    '"Offer Letters"': '"Cartas de Oferta"',
    '"Candidate"': '"Candidato"',
    '"Candidates"': '"Candidatos"',
    '"Invoice"': '"Fatura"',
    '"Invoices"': '"Faturas"',
    '"Invoice Item"': '"Item da Fatura"',
    '"Invoice Items"': '"Itens da Fatura"',
    '"Estimate"': '"Orçamento"',
    '"Estimates"': '"Orçamentos"',
    '"Proposal"': '"Proposta"',
    '"Proposals"': '"Propostas"',
    '"Expense"': '"Despesa"',
    '"Expenses"': '"Despesas"',
    '"Payment Gateway"': '"Gateway de Pagamento"',
    '"Payment Gateways"': '"Gateways de Pagamento"',
    '"Payment"': '"Pagamento"',
    '"Payments"': '"Pagamentos"',
    '"Company"': '"Empresa"',
    '"Companies"': '"Empresas"',

    # help_text translations
    '"Employee ID code"': '"Código de ID do Funcionário"',
    '"Annual leave days entitlement"': '"Dias de licença anual permitidos"',
    '"Hours worked beyond shift hours"': '"Horas trabalhadas além do horário de turno"',
    '"Comma-separated skills"': '"Habilidades separadas por vírgulas"',
    '"Zoom/Google Meet link"': '"Link do Zoom/Google Meet"',
    '"Internal note, not visible to customer"': '"Nota interna, não visível para o cliente"',
    '"Pin to top of notice board"': '"Fixar no topo do quadro de avisos"',
    '"Max users per company, null=unlimited"': '"Máximo de usuários por empresa, nulo=ilimitado"',
    '"Max storage in GB, null=unlimited"': '"Armazenamento máximo em GB, nulo=ilimitado"',
    '"Years of experience"': '"Anos de experiência"',
    '"Maximum number of times coupon can be used"': '"Número máximo de vezes que o cupom pode ser usado"',
    '"Company name"': '"Nome da Empresa"',
    '"Unique identifier for URL (e.g., acme-corp)"': '"Identificador único para URL (ex: acme-corp)"',
    '"Company description"': '"Descrição da Empresa"',
    '"Company primary email"': '"E-mail principal da empresa"',
    '"Company logo"': '"Logo da empresa"',
    '"Company timezone"': '"Fuso horário da empresa"',
    '"Default currency code (ISO 4217)"': '"Código de moeda padrão (ISO 4217)"',
    '"Industry vertical (e.g., Technology, Healthcare, Finance)"': '"Vertical da indústria (ex: Tecnologia, Saúde, Finanças)"',
    '"If True, can be used as template for multiple employees"': '"Se Verdadeiro, pode ser usado como modelo para vários funcionários"',
    '"Month of payslip (first day)"': '"Mês do contracheque (primeiro dia)"',
    '"1-5 star rating"': '"Classificação de 1-5 estrelas"',
    '"Closing probability %"': '"Probabilidade de fechamento %"',
    '"Domain name (e.g., tenant.example.com)"': '"Nome de domínio (ex: tenant.example.com)"',
    '"The company this domain belongs to"': '"A empresa a qual este domínio pertence"',
}

# Choices translations
CHOICES_TRANSLATIONS = {
    # Employee gender choices
    '("Male", "Male")': '("male", "Masculino")',
    '("Female", "Female")': '("female", "Feminino")',
    '("Other", "Other")': '("other", "Outro")',
    '("Prefer not to say", "Prefer not to say")': '("prefer_not_to_say", "Prefiro não responder")',
    
    # Employment type
    '("Permanent", "Permanent")': '("permanent", "Permanente")',
    '("Contract", "Contract")': '("contract", "Contrato")',
    '("Temporary", "Temporary")': '("temporary", "Temporário")',
    '("Internship", "Internship")': '("internship", "Estágio")',
    '("Freelance", "Freelance")': '("freelance", "Freelancer")',
    
    # Status choices
    '("Active", "Active")': '("active", "Ativo")',
    '("Inactive", "Inactive")': '("inactive", "Inativo")',
    '("On Leave", "On Leave")': '("on_leave", "Em Licença")',
    '("Suspended", "Suspended")': '("suspended", "Suspenso")',
    '("Terminated", "Terminated")': '("terminated", "Encerrado")',
    
    # Draft/Submitted/Approved/Rejected pattern
    '("Draft", "Draft")': '("draft", "Rascunho")',
    '("Submitted", "Submitted")': '("submitted", "Submetido")',
    '("Approved", "Approved")': '("approved", "Aprovado")',
    '("Rejected", "Rejected")': '("rejected", "Rejeitado")',
    
    # Leave status
    '("Cancelled", "Cancelled")': '("cancelled", "Cancelado")',
    
    # Shift/Present/Absent pattern
    '("Present", "Present")': '("present", "Presente")',
    '("Absent", "Absent")': '("absent", "Ausente")',
    '("Half Day", "Half Day")': '("half_day", "Meio Período")',
    '("Late", "Late")': '("late", "Atrasado")',
    
    # Priority choices
    '("Low", "Low")': '("low", "Baixa")',
    '("Medium", "Medium")': '("medium", "Média")',
    '("High", "High")': '("high", "Alta")',
    '("Urgent", "Urgent")': '("urgent", "Urgente")',
}

def translate_file(file_path):
    """Translate a single Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply translations
        for english, portuguese in TRANSLATIONS.items():
            content = content.replace(english, portuguese)
        
        for english, portuguese in CHOICES_TRANSLATIONS.items():
            content = content.replace(english, portuguese)
        
        # Only write if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Translate all model files."""
    apps_dir = "apps"
    translated_count = 0
    
    for app in os.listdir(apps_dir):
        models_file = os.path.join(apps_dir, app, "models.py")
        if os.path.exists(models_file):
            if translate_file(models_file):
                print(f"✅ Translated: {models_file}")
                translated_count += 1
            else:
                print(f"⏭️  Skipped (no changes): {models_file}")
    
    print(f"\n✅ Total files translated: {translated_count}")

if __name__ == "__main__":
    main()
