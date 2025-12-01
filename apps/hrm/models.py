"""
HRM (Human Resource Management) App Models

Sub-modules:
- Employees: Employee profiles, departments, designations
- Leaves: Leave/absence management with types and approvals
- Attendance: Time tracking, shifts, biometric integration
- Payroll: Salary structures, payslips, deductions
- Performance: Appraisals, OKRs, performance metrics
"""

from django.db import models
from apps.core.models import TenantAwareModel, User


# ============================================================================
# 1. EMPLOYEES SUB-MODULE
# ============================================================================

class Department(TenantAwareModel):
    """Company departments."""

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    head = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="department_head",
    )

    class Meta:
        verbose_name = "Department"
        verbose_name_plural = "Departments"
        unique_together = ["company", "name"]

    def __str__(self):
        return self.name


class Designation(TenantAwareModel):
    """Job titles/designations."""

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    level = models.CharField(
        max_length=50,
        choices=[
            ("entry", "Entry Level"),
            ("mid", "Mid Level"),
            ("senior", "Senior"),
            ("lead", "Lead"),
            ("manager", "Manager"),
            ("director", "Director"),
            ("executive", "Executive"),
        ],
    )

    class Meta:
        verbose_name = "Designation"
        verbose_name_plural = "Designations"
        unique_together = ["company", "name"]

    def __str__(self):
        return self.name


class Employee(TenantAwareModel):
    """Employee records (extends User model)."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="employee")
    employee_id = models.CharField(
        max_length=50,
        unique=True,
        help_text="Employee ID code",
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        related_name="employees",
    )
    designation = models.ForeignKey(
        Designation,
        on_delete=models.SET_NULL,
        null=True,
        related_name="employees",
    )
    reporting_manager = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subordinates",
    )
    date_of_joining = models.DateField()
    date_of_birth = models.DateField()
    gender = models.CharField(
        max_length=20,
        choices=[
            ("male", "Male"),
            ("female", "Female"),
            ("other", "Other"),
            ("prefer_not_to_say", "Prefer not to say"),
        ],
    )
    nationality = models.CharField(max_length=100)
    employment_type = models.CharField(
        max_length=50,
        choices=[
            ("permanent", "Permanent"),
            ("contract", "Contract"),
            ("temporary", "Temporary"),
            ("internship", "Internship"),
            ("freelance", "Freelance"),
        ],
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ("active", "Active"),
            ("on_leave", "On Leave"),
            ("suspended", "Suspended"),
            ("terminated", "Terminated"),
        ],
        default="active",
    )

    class Meta:
        verbose_name = "Employee"
        verbose_name_plural = "Employees"

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_id})"


# ============================================================================
# 2. LEAVES SUB-MODULE
# ============================================================================

class LeaveType(TenantAwareModel):
    """Types of leaves (Annual, Sick, Casual, etc.)."""

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    annual_entitlement = models.IntegerField(
        default=20,
        help_text="Annual leave days entitlement",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Leave Type"
        verbose_name_plural = "Leave Types"
        unique_together = ["company", "code"]

    def __str__(self):
        return self.name


class Leave(TenantAwareModel):
    """Leave/absence requests."""

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("cancelled", "Cancelled"),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="leaves",
    )
    leave_type = models.ForeignKey(
        LeaveType,
        on_delete=models.PROTECT,
        related_name="leaves",
    )
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_leaves",
    )
    approval_comments = models.TextField(blank=True)
    approval_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Leave"
        verbose_name_plural = "Leaves"

    def __str__(self):
        return f"{self.employee} - {self.leave_type} ({self.start_date} to {self.end_date})"


# ============================================================================
# 3. ATTENDANCE SUB-MODULE
# ============================================================================

class Shift(TenantAwareModel):
    """Work shifts configuration."""

    name = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Shift"
        verbose_name_plural = "Shifts"
        unique_together = ["company", "name"]

    def __str__(self):
        return f"{self.name} ({self.start_time} - {self.end_time})"


class Attendance(TenantAwareModel):
    """Daily attendance records."""

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="attendance_records",
    )
    date = models.DateField()
    shift = models.ForeignKey(
        Shift,
        on_delete=models.SET_NULL,
        null=True,
        related_name="attendance",
    )
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("present", "Present"),
            ("absent", "Absent"),
            ("half_day", "Half Day"),
            ("late", "Late"),
            ("on_leave", "On Leave"),
        ],
    )
    notes = models.TextField(blank=True)
    overtime_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Hours worked beyond shift hours",
    )

    class Meta:
        verbose_name = "Attendance"
        verbose_name_plural = "Attendance Records"
        unique_together = ["company", "employee", "date"]

    def __str__(self):
        return f"{self.employee} - {self.date} ({self.status})"


# ============================================================================
# 4. PAYROLL SUB-MODULE
# ============================================================================

class SalaryStructure(TenantAwareModel):
    """Salary structure templates for employees."""

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    base_salary = models.DecimalField(max_digits=12, decimal_places=2)
    is_template = models.BooleanField(
        default=True,
        help_text="If True, can be used as template for multiple employees",
    )

    class Meta:
        verbose_name = "Salary Structure"
        verbose_name_plural = "Salary Structures"
        unique_together = ["company", "name"]

    def __str__(self):
        return f"{self.name} (${self.base_salary})"


class EmployeeSalary(TenantAwareModel):
    """Employee salary assignment."""

    employee = models.OneToOneField(
        Employee,
        on_delete=models.CASCADE,
        related_name="salary",
    )
    salary_structure = models.ForeignKey(
        SalaryStructure,
        on_delete=models.PROTECT,
        related_name="employees",
    )
    base_salary = models.DecimalField(max_digits=12, decimal_places=2)
    effective_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "Employee Salary"
        verbose_name_plural = "Employee Salaries"

    def __str__(self):
        return f"{self.employee} - ${self.base_salary}"


class Payslip(TenantAwareModel):
    """Monthly payslips."""

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="payslips",
    )
    month = models.DateField(help_text="Month of payslip (first day)")
    salary_amount = models.DecimalField(max_digits=12, decimal_places=2)
    deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=[
            ("draft", "Draft"),
            ("approved", "Approved"),
            ("paid", "Paid"),
        ],
        default="draft",
    )
    paid_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Payslip"
        verbose_name_plural = "Payslips"
        unique_together = ["company", "employee", "month"]

    def __str__(self):
        return f"{self.employee} - {self.month.strftime('%B %Y')}"


# ============================================================================
# 5. PERFORMANCE SUB-MODULE
# ============================================================================

class PerformanceGoal(TenantAwareModel):
    """OKRs and performance goals."""

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="goals",
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    target_value = models.CharField(max_length=255)
    achieved_value = models.CharField(max_length=255, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("not_started", "Not Started"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
            ("on_track", "On Track"),
            ("at_risk", "At Risk"),
        ],
        default="not_started",
    )
    start_date = models.DateField()
    end_date = models.DateField()
    progress_percentage = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Performance Goal"
        verbose_name_plural = "Performance Goals"

    def __str__(self):
        return f"{self.employee} - {self.title}"


class PerformanceReview(TenantAwareModel):
    """Performance review/appraisal."""

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="performance_reviews",
    )
    reviewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="performance_reviews_given",
    )
    review_period_start = models.DateField()
    review_period_end = models.DateField()
    rating = models.IntegerField(
        choices=[
            (1, "Poor"),
            (2, "Below Average"),
            (3, "Average"),
            (4, "Good"),
            (5, "Excellent"),
        ],
    )
    comments = models.TextField()
    strengths = models.TextField(blank=True)
    areas_for_improvement = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("approved", "Approved"),
            ("completed", "Completed"),
        ],
        default="draft",
    )

    class Meta:
        verbose_name = "Performance Review"
        verbose_name_plural = "Performance Reviews"

    def __str__(self):
        return f"{self.employee} - Review {self.review_period_start.year}"
