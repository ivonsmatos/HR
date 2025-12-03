"""
WORK (Projects & Tasks) App Models

Sub-modules:
- Projects: Project management and team allocation
- Tasks: Task tracking, Kanban board, status management
- TimeLogs: Time tracking by task and project
- Contracts: Contract management and versioning
"""

from django.db import models
from apps.core.models import TenantAwareModel, User
from apps.hrm.models import Employee


# ============================================================================
# 1. PROJECTS SUB-MODULE
# ============================================================================

class Project(TenantAwareModel):
    """Project records."""

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    slug = models.SlugField(max_length=100, unique=True)
    
    # Client Reference
    client = models.ForeignKey(
        "crm.Client",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="projects",
    )
    
    # Team
    project_lead = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="projects_lead",
    )
    
    # Timeline
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ("planning", "Planning"),
            ("active", "Active"),
            ("paused", "Paused"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        default="planning",
    )
    
    # Budget
    budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default="BRL")
    
    # Progress
    completion_percentage = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Projeto"
        verbose_name_plural = "Projetos"
        unique_together = ["company", "slug"]

    def __str__(self):
        return self.name


class ProjectMember(TenantAwareModel):
    """Project team members."""

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="members",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="project_memberships",
    )
    role = models.CharField(
        max_length=50,
        choices=[
            ("lead", "Project Lead"),
            ("developer", "Developer"),
            ("designer", "Designer"),
            ("qa", "QA"),
            ("manager", "Manager"),
            ("contributor", "Contributor"),
        ],
    )
    allocation_percentage = models.IntegerField(default=100)
    joined_date = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = "Membro do Projeto"
        verbose_name_plural = "Membros do Projeto"
        unique_together = ["company", "project", "user"]

    def __str__(self):
        return f"{self.user.username} - {self.project.name} ({self.role})"


# ============================================================================
# 2. TASKS SUB-MODULE
# ============================================================================

class Task(TenantAwareModel):
    """Task records."""

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Assignment
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
    )
    
    # Status & Priority
    status = models.CharField(
        max_length=20,
        choices=[
            ("backlog", "Backlog"),
            ("todo", "To Do"),
            ("in_progress", "In Progress"),
            ("review", "Review"),
            ("done", "Done"),
        ],
        default="backlog",
    )
    priority = models.CharField(
        max_length=20,
        choices=[
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High"),
            ("urgent", "Urgent"),
        ],
        default="medium",
    )
    
    # Timeline
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    estimated_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
    )
    
    # Kanban
    kanban_order = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Tarefa"
        verbose_name_plural = "Tarefas"
        ordering = ["kanban_order", "-created_at"]

    def __str__(self):
        return f"{self.title} [{self.project.name}]"


class TaskComment(TenantAwareModel):
    """Task comments."""

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="task_comments",
    )
    content = models.TextField()

    class Meta:
        verbose_name = "Comentário na Tarefa"
        verbose_name_plural = "Comentários nas Tarefas"

    def __str__(self):
        return f"Comment on {self.task.title}"


# ============================================================================
# 3. TIME LOGS SUB-MODULE
# ============================================================================

class TimeLog(TenantAwareModel):
    """Time spent on tasks."""

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="timelogs",
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="timelogs",
    )
    date = models.DateField()
    hours = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField(blank=True)
    
    # Billing
    is_billable = models.BooleanField(default=True)
    billable_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name = "Registro de Tempo"
        verbose_name_plural = "Registros de Tempo"
        unique_together = ["company", "task", "employee", "date"]

    def __str__(self):
        return f"{self.employee} - {self.task.title} ({self.hours}h on {self.date})"


# ============================================================================
# 4. CONTRACTS SUB-MODULE
# ============================================================================

class Contract(TenantAwareModel):
    """Client/project contracts."""

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="contracts",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Type & Value
    contract_type = models.CharField(
        max_length=50,
        choices=[
            ("fixed_price", "Fixed Price"),
            ("hourly", "Hourly"),
            ("retainer", "Retainer"),
            ("T&M", "Time & Material"),
        ],
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="BRL")
    
    # Dates
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ("draft", "Draft"),
            ("signed", "Signed"),
            ("active", "Active"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
    )
    
    # Documents
    contract_document = models.FileField(upload_to="contracts/", null=True, blank=True)
    signed_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Contrato"
        verbose_name_plural = "Contratos"

    def __str__(self):
        return f"{self.title} - {self.project.name}"
