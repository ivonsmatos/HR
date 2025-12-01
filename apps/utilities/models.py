"""
UTILITIES (Utilities & Tools) App Models

Sub-modules:
- Tickets: Helpdesk and support tickets
- Assets: Asset management (hardware/software)
- Events: Calendar events and conferences
- Messages: Internal messaging
- NoticeBboard: Notice board for announcements
"""

from django.db import models
from apps.core.models import TenantAwareModel, User
from apps.hrm.models import Employee


# ============================================================================
# 1. TICKETS SUB-MODULE
# ============================================================================

class Ticket(TenantAwareModel):
    """Support/helpdesk tickets."""

    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("urgent", "Urgent"),
    ]

    STATUS_CHOICES = [
        ("open", "Open"),
        ("in_progress", "In Progress"),
        ("waiting_for_customer", "Waiting for Customer"),
        ("resolved", "Resolved"),
        ("closed", "Closed"),
    ]

    ticket_number = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    
    # Assignment
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="tickets_created",
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tickets_assigned",
    )
    
    # Status
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default="medium")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")
    
    # Category
    category = models.CharField(
        max_length=100,
        choices=[
            ("technical", "Technical"),
            ("billing", "Billing"),
            ("feature_request", "Feature Request"),
            ("bug_report", "Bug Report"),
            ("other", "Other"),
        ],
    )
    
    # Timeline
    due_date = models.DateField(null=True, blank=True)
    resolved_date = models.DateTimeField(null=True, blank=True)
    
    attachment = models.FileField(upload_to="ticket_attachments/", null=True, blank=True)

    class Meta:
        verbose_name = "Ticket"
        verbose_name_plural = "Tickets"
        unique_together = ["company", "ticket_number"]

    def __str__(self):
        return f"Ticket {self.ticket_number}: {self.title}"


class TicketReply(TenantAwareModel):
    """Ticket replies/comments."""

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="replies",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="ticket_replies",
    )
    content = models.TextField()
    attachment = models.FileField(upload_to="ticket_attachments/", null=True, blank=True)
    is_internal = models.BooleanField(default=False, help_text="Internal note, not visible to customer")

    class Meta:
        verbose_name = "Ticket Reply"
        verbose_name_plural = "Ticket Replies"

    def __str__(self):
        return f"Reply to Ticket {self.ticket.ticket_number}"


# ============================================================================
# 2. ASSETS SUB-MODULE
# ============================================================================

class Asset(TenantAwareModel):
    """Company assets (hardware/software)."""

    ASSET_TYPE_CHOICES = [
        ("hardware", "Hardware"),
        ("software", "Software"),
        ("furniture", "Furniture"),
        ("vehicle", "Vehicle"),
        ("other", "Other"),
    ]

    STATUS_CHOICES = [
        ("available", "Available"),
        ("in_use", "In Use"),
        ("maintenance", "Maintenance"),
        ("disposed", "Disposed"),
        ("lost", "Lost"),
    ]

    name = models.CharField(max_length=255)
    asset_type = models.CharField(max_length=50, choices=ASSET_TYPE_CHOICES)
    serial_number = models.CharField(max_length=100, unique=True)
    
    # Details
    description = models.TextField(blank=True)
    brand = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)
    
    # Financial
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2)
    current_value = models.DecimalField(max_digits=12, decimal_places=2)
    purchase_date = models.DateField()
    warranty_expiry = models.DateField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="available")
    location = models.CharField(max_length=255, blank=True)
    
    # Allocation
    assigned_to = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assets",
    )
    assignment_date = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "Asset"
        verbose_name_plural = "Assets"
        unique_together = ["company", "serial_number"]

    def __str__(self):
        return f"{self.name} ({self.serial_number})"


# ============================================================================
# 3. EVENTS SUB-MODULE
# ============================================================================

class Event(TenantAwareModel):
    """Company events and meetings."""

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Schedule
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    # Type
    event_type = models.CharField(
        max_length=50,
        choices=[
            ("meeting", "Meeting"),
            ("conference", "Conference"),
            ("training", "Training"),
            ("social", "Social"),
            ("holiday", "Holiday"),
            ("other", "Other"),
        ],
    )
    
    # Location
    location = models.CharField(max_length=255, blank=True)
    is_virtual = models.BooleanField(default=False)
    meeting_link = models.URLField(blank=True, help_text="Zoom/Google Meet link")
    
    # Organizer
    organizer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="events_organized",
    )
    
    # Attendees
    attendees = models.ManyToManyField(
        User,
        related_name="events_attending",
        blank=True,
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ("scheduled", "Scheduled"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        default="scheduled",
    )

    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"
        ordering = ["-start_date"]

    def __str__(self):
        return self.title


# ============================================================================
# 4. MESSAGES SUB-MODULE
# ============================================================================

class Message(TenantAwareModel):
    """Internal messaging system."""

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="messages_sent",
    )
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="messages_received",
    )
    subject = models.CharField(max_length=255, blank=True)
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False, related_name="archived_messages")

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Message from {self.sender.username} to {self.recipient.username}"


# ============================================================================
# 5. NOTICE BOARD SUB-MODULE
# ============================================================================

class Notice(TenantAwareModel):
    """Notice board announcements."""

    title = models.CharField(max_length=255)
    content = models.TextField()
    
    # Visibility
    category = models.CharField(
        max_length=50,
        choices=[
            ("general", "General"),
            ("hr", "HR"),
            ("technical", "Technical"),
            ("important", "Important"),
            ("event", "Event"),
        ],
    )
    
    # Publication
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notices_created",
    )
    publish_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    # Priority
    is_pinned = models.BooleanField(default=False, help_text="Pin to top of notice board")
    priority = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Notice"
        verbose_name_plural = "Notices"
        ordering = ["-is_pinned", "-publish_date"]

    def __str__(self):
        return self.title
