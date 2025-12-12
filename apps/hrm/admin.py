"""HRM app admin configuration."""
from django.contrib import admin
from .models import (
    Department, Designation, Employee, LeaveType, Leave, Shift, Attendance,
    SalaryStructure, EmployeeSalary, Payslip, PerformanceGoal, PerformanceReview
)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ["name", "company", "head"]
    list_filter = ["company"]
    search_fields = ["name"]


@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    list_display = ["name", "company", "level"]
    list_filter = ["company", "level"]
    search_fields = ["name"]


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ["employee_id", "user", "department", "designation", "status"]
    list_filter = ["company", "department", "status", "employment_type"]
    search_fields = ["employee_id", "user__username", "user__email"]


@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "company", "annual_entitlement", "is_active"]
    list_filter = ["company", "is_active"]
    search_fields = ["name", "code"]


@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = ["employee", "leave_type", "start_date", "end_date", "status"]
    list_filter = ["company", "status", "leave_type"]
    search_fields = ["employee__user__username"]


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ["name", "company", "start_time", "end_time"]
    list_filter = ["company"]
    search_fields = ["name"]


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ["employee", "date", "status", "company"]
    list_filter = ["company", "status", "date"]
    search_fields = ["employee__user__username"]
    date_hierarchy = "date"


@admin.register(SalaryStructure)
class SalaryStructureAdmin(admin.ModelAdmin):
    list_display = ["name", "company", "base_salary", "is_template"]
    list_filter = ["company", "is_template"]
    search_fields = ["name"]


@admin.register(EmployeeSalary)
class EmployeeSalaryAdmin(admin.ModelAdmin):
    list_display = ["employee", "company", "base_salary", "effective_date"]
    list_filter = ["company", "effective_date"]
    search_fields = ["employee__user__username"]


@admin.register(Payslip)
class PayslipAdmin(admin.ModelAdmin):
    list_display = ["employee", "month", "net_amount", "status"]
    list_filter = ["company", "status", "month"]
    search_fields = ["employee__user__username"]


@admin.register(PerformanceGoal)
class PerformanceGoalAdmin(admin.ModelAdmin):
    list_display = ["employee", "title", "status", "progress_percentage"]
    list_filter = ["company", "status"]
    search_fields = ["title", "employee__user__username"]


@admin.register(PerformanceReview)
class PerformanceReviewAdmin(admin.ModelAdmin):
    list_display = ["employee", "reviewer", "rating", "status"]
    list_filter = ["company", "status", "rating"]
    search_fields = ["employee__user__username"]
