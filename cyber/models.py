from django.db import models
from django.utils import timezone


class Users(models.Model):
    """Registered application users (bcrypt-hashed passwords)."""

    id = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    password_hash = models.CharField(max_length=255)
    role = models.CharField(max_length=20, default="user")

    class Meta:
        db_table = 'users'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(role__in=["user", "admin"]),
                name="users_role_valid",
            ),
        ]


class CyberIncidents(models.Model):
    """Cybersecurity incident records."""

    incident_id = models.BigIntegerField(primary_key=True)
    timestamp = models.DateTimeField()
    severity = models.CharField(max_length=20, default="Medium")
    category = models.CharField(max_length=50, default="Unknown")
    status = models.CharField(max_length=20, default="Open")
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'cyber_incidents'
        indexes = [
            models.Index(fields=['severity']),
            models.Index(fields=['status']),
            models.Index(fields=['category']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    severity__in=["Low", "Medium", "High", "Critical"]),
                name="cyber_incidents_severity_valid",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    status__in=["Open", "In Progress", "Resolved", "Closed"]),
                name="cyber_incidents_status_valid",
            ),
        ]


class DatasetsMetadata(models.Model):
    """Metadata describing uploaded datasets."""

    dataset_id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    rows = models.IntegerField(default=0, db_column='row_count')
    columns = models.IntegerField(default=0, db_column='column_count')
    uploaded_by = models.CharField(max_length=150, blank=True, null=True)
    upload_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'datasets_metadata'
        indexes = [
            models.Index(fields=['uploaded_by']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(rows__gte=0), name="datasets_metadata_rows_valid"),
            models.CheckConstraint(
                condition=models.Q(columns__gte=0),
                name="datasets_metadata_columns_valid"),
        ]


class ItTickets(models.Model):
    """IT support tickets."""

    ticket_id = models.BigIntegerField(primary_key=True)
    priority = models.CharField(max_length=20, default="Medium")
    description = models.TextField()
    status = models.CharField(max_length=20, default="Open")
    assigned_to = models.CharField(max_length=150, blank=True, null=True)
    created_at = models.DateTimeField()
    resolution_time_hours = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'it_tickets'
        indexes = [
            models.Index(fields=['priority']),
            models.Index(fields=['status']),
            models.Index(fields=['assigned_to']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    priority__in=["Low", "Medium", "High", "Critical"]),
                name="it_tickets_priority_valid",
            ),
            models.CheckConstraint(
                condition=models.Q(status__in=[
                    "Open", "In Progress", "Resolved", "Closed",
                    "Waiting for User"]),
                name="it_tickets_status_valid",
            ),
            models.CheckConstraint(
                condition=models.Q(resolution_time_hours__gte=0)
                | models.Q(resolution_time_hours__isnull=True),
                name="it_tickets_resolution_valid",
            ),
        ]


class AuditTrail(models.Model):
    """Mirror of the external monitored system's audit log (no labels).

    ``user_id`` refers to synthetic identities in the source audit (1-30) and
    deliberately has no foreign key to ``users``.
    """

    id = models.BigAutoField(primary_key=True)
    user_id = models.IntegerField(blank=True, null=True)
    action = models.CharField(max_length=50)
    resource = models.CharField(max_length=50, blank=True, null=True)
    method = models.CharField(max_length=10, blank=True, null=True)
    endpoint = models.CharField(max_length=255, blank=True, null=True)
    ip_address = models.CharField(max_length=45, blank=True, null=True)
    user_agent = models.CharField(max_length=500, blank=True, null=True)
    session_id = models.CharField(max_length=64, blank=True, null=True)
    status_code = models.IntegerField(blank=True, null=True)
    response_time_ms = models.IntegerField(blank=True, null=True)
    metadata = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField()

    class Meta:
        db_table = 'audit_trail'
        indexes = [
            models.Index(fields=['user_id']),
            models.Index(fields=['action']),
            models.Index(fields=['created_at']),
            models.Index(fields=['session_id']),
        ]


class AnalyticalReports(models.Model):
    """Output of the AI monitor: one row per answered question."""

    id = models.BigAutoField(primary_key=True)
    run_id = models.CharField(max_length=50)
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField()

    class Meta:
        db_table = 'analytical_reports'
        indexes = [
            models.Index(fields=['run_id']),
        ]


class AiMonitorState(models.Model):
    """Key/value store for the AI monitor's scan cursor."""

    key = models.CharField(max_length=100, primary_key=True)
    value = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ai_monitor_state'
