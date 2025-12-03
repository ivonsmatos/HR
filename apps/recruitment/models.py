"""
RECRUITMENT (ATS - Applicant Tracking System) App Models

Sub-modules:
- Jobs: Job postings and management
- JobApplications: Application tracking
- Interviews: Interview scheduling
- OfferLetters: Offer letter generation
- Candidates: Candidate database
"""

from django.db import models
from apps.core.models import TenantAwareModel, User


# ============================================================================
# 1. JOBS SUB-MODULE
# ============================================================================

class Job(TenantAwareModel):
    """Job postings."""

    title = models.CharField(max_length=255)
    description = models.TextField()
    requirements = models.TextField()
    
    # Department & Position
    department = models.ForeignKey(
        "hrm.Department",
        on_delete=models.SET_NULL,
        null=True,
        related_name="open_jobs",
    )
    designation = models.ForeignKey(
        "hrm.Designation",
        on_delete=models.SET_NULL,
        null=True,
        related_name="open_jobs",
    )
    
    # Hiring Manager
    hiring_manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="jobs_managing",
    )
    
    # Position Details
    experience_required = models.IntegerField(default=0, help_text="Anos de experiência")
    salary_range_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    salary_range_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default="BRL")
    positions_open = models.IntegerField(default=1)
    
    # Dates
    posted_date = models.DateField(auto_now_add=True)
    closing_date = models.DateField()
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ("draft", "Draft"),
            ("published", "Published"),
            ("closed", "Closed"),
            ("on_hold", "On Hold"),
        ],
        default="draft",
    )
    
    # Employment Type
    employment_type = models.CharField(
        max_length=50,
        choices=[
            ("full_time", "Full Time"),
            ("part_time", "Part Time"),
            ("contract", "Contrato"),
            ("internship", "Internship"),
        ],
    )
    
    # Location
    location = models.CharField(max_length=255)
    is_remote = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Vaga/Emprego"
        verbose_name_plural = "Vagas/Empregos"

    def __str__(self):
        return self.title


# ============================================================================
# 2. JOB APPLICATIONS SUB-MODULE
# ============================================================================

class JobApplication(TenantAwareModel):
    """Job applications."""

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="applications",
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    
    # Application
    resume = models.FileField(upload_to="job_applications/resumes/")
    cover_letter = models.TextField(blank=True)
    application_date = models.DateTimeField(auto_now_add=True)
    
    # Pipeline Status
    status = models.CharField(
        max_length=20,
        choices=[
            ("applied", "Applied"),
            ("screening", "Screening"),
            ("interview", "Interview"),
            ("offered", "Offered"),
            ("hired", "Hired"),
            ("rejected", "Rejected"),
            ("withdrew", "Withdrew"),
        ],
        default="applied",
    )
    
    # Rating
    rating = models.IntegerField(null=True, blank=True, help_text="Classificação de 1-5 estrelas")
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Candidatura/Solicitação de Emprego"
        verbose_name_plural = "Candidaturas/Solicitações de Emprego"

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.job.title}"


# ============================================================================
# 3. INTERVIEWS SUB-MODULE
# ============================================================================

class InterviewSchedule(TenantAwareModel):
    """Interview scheduling."""

    application = models.ForeignKey(
        JobApplication,
        on_delete=models.CASCADE,
        related_name="interviews",
    )
    
    interview_type = models.CharField(
        max_length=50,
        choices=[
            ("phone", "Phone"),
            ("video", "Video"),
            ("in_person", "In Person"),
            ("group", "Group"),
        ],
    )
    
    # Schedule
    scheduled_date = models.DateTimeField()
    duration_minutes = models.IntegerField(default=60)
    
    # Interviewer(s)
    interviewers = models.ManyToManyField(
        User,
        related_name="interview_schedules",
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ("scheduled", "Scheduled"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        default="scheduled",
    )
    
    # Meeting Details
    meeting_link = models.URLField(blank=True, help_text="Link do Zoom/Google Meet")
    location = models.CharField(max_length=255, blank=True)
    
    # Feedback
    feedback = models.TextField(blank=True)
    result = models.CharField(
        max_length=20,
        choices=[
            ("pass", "Pass"),
            ("fail", "Fail"),
            ("maybe", "Maybe"),
        ],
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Agendamento de Entrevista"
        verbose_name_plural = "Agendamentos de Entrevista"

    def __str__(self):
        return f"Interview: {self.application.first_name} - {self.scheduled_date}"


# ============================================================================
# 4. OFFER LETTERS SUB-MODULE
# ============================================================================

class OfferLetter(TenantAwareModel):
    """Offer letters."""

    application = models.ForeignKey(
        JobApplication,
        on_delete=models.CASCADE,
        related_name="offer_letters",
    )
    
    offer_number = models.CharField(max_length=50, unique=True)
    
    # Details
    position_title = models.CharField(max_length=255)
    department = models.CharField(max_length=100)
    salary = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="BRL")
    
    # Dates
    offer_date = models.DateField(auto_now_add=True)
    joining_date = models.DateField()
    expiry_date = models.DateField()
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ("draft", "Draft"),
            ("sent", "Sent"),
            ("accepted", "Accepted"),
            ("rejected", "Rejected"),
            ("expired", "Expired"),
        ],
        default="draft",
    )
    
    # Document
    offer_letter_file = models.FileField(upload_to="offer_letters/", null=True, blank=True)
    acceptance_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Carta de Oferta"
        verbose_name_plural = "Cartas de Oferta"
        unique_together = ["company", "offer_number"]

    def __str__(self):
        return f"Offer {self.offer_number} - {self.application.first_name} {self.application.last_name}"


# ============================================================================
# 5. CANDIDATES SUB-MODULE
# ============================================================================

class Candidate(TenantAwareModel):
    """Candidate database (talent pool)."""

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    
    # Profile
    current_company = models.CharField(max_length=255, blank=True)
    current_designation = models.CharField(max_length=255, blank=True)
    experience_years = models.IntegerField(default=0)
    
    # Skills
    skills = models.TextField(blank=True, help_text="Habilidades separadas por vírgulas")
    
    # Location
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ("active", "Active"),
            ("interested", "Interested"),
            ("not_interested", "Not Interested"),
            ("hired", "Hired"),
            ("archived", "Archived"),
        ],
        default="active",
    )
    
    # Notes
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Candidato"
        verbose_name_plural = "Candidatos"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
