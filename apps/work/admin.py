"""Work app admin configuration."""
from django.contrib import admin
from .models import Project, ProjectMember, Task, TaskComment, TimeLog, Contract


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["name", "client", "project_lead", "status", "completion_percentage"]
    list_filter = ["company", "status", "start_date"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    list_display = ["user", "project", "role", "allocation_percentage"]
    list_filter = ["company", "role"]
    search_fields = ["project__name", "user__username"]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ["title", "project", "assigned_to", "status", "priority", "due_date"]
    list_filter = ["company", "status", "priority"]
    search_fields = ["title", "project__name"]


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ["task", "author", "created_at"]
    list_filter = ["company", "created_at"]
    search_fields = ["task__title", "author__username"]


@admin.register(TimeLog)
class TimeLogAdmin(admin.ModelAdmin):
    list_display = ["employee", "task", "date", "hours", "is_billable"]
    list_filter = ["company", "date", "is_billable"]
    search_fields = ["employee__user__username", "task__title"]
    date_hierarchy = "date"


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ["title", "project", "contract_type", "amount", "status"]
    list_filter = ["company", "status", "contract_type"]
    search_fields = ["title", "project__name"]
