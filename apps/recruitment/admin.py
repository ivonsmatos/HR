"""Recruitment app admin configuration."""
from django.contrib import admin
from .models import Job, JobApplication, InterviewSchedule, OfferLetter, Candidate


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ["title", "department", "positions_open", "status", "closing_date"]
    list_filter = ["company", "status", "employment_type"]
    search_fields = ["title", "description"]


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "job", "status", "application_date"]
    list_filter = ["company", "status", "job"]
    search_fields = ["first_name", "last_name", "email"]
    date_hierarchy = "application_date"


@admin.register(InterviewSchedule)
class InterviewScheduleAdmin(admin.ModelAdmin):
    list_display = ["application", "interview_type", "scheduled_date", "status"]
    list_filter = ["company", "status", "interview_type"]
    search_fields = ["application__first_name"]


@admin.register(OfferLetter)
class OfferLetterAdmin(admin.ModelAdmin):
    list_display = ["offer_number", "application", "position_title", "status"]
    list_filter = ["company", "status"]
    search_fields = ["offer_number", "application__first_name"]


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "current_designation", "experience_years", "status"]
    list_filter = ["company", "status"]
    search_fields = ["first_name", "last_name", "email"]
