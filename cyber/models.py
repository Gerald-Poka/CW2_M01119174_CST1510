from django.db import models
from django.utils import timezone

# Every table carries the same four audit columns, always defined LAST:
#   created_at   - stamped automatically on insert (the value shown for a new row)
#   created_by   - the User who created the row (nullable, system-seeded rows have None)
#   updated_at   - refreshed automatically on every update
#   updated_by   - the User who last updated the row (nullable)


class Role(models.Model):
    """Lookup table of application roles (Administrator, Normal Staff)."""

    id = models.BigAutoField(primary_key=True)
    role_name = models.CharField(max_length=50, unique=True)

    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(
        'User', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='%(class)s_created')
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        'User', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='%(class)s_updated')

    class Meta:
        db_table = 'roles'
        ordering = ['id']

    def __str__(self):
        return self.role_name


class User(models.Model):
    """Login credentials only — all other profile data lives in ``staff``."""

    id = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    password_hash = models.CharField(max_length=255)
    role = models.ForeignKey(Role, on_delete=models.PROTECT,
                             related_name='users')
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='%(class)s_created')
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='%(class)s_updated')

    class Meta:
        db_table = 'user'

    @property
    def role_name(self):
        return self.role.role_name if self.role else 'Normal Staff'

    def __str__(self):
        return self.username


class Staff(models.Model):
    """Complete user details, linked one-to-one to a login account."""

    id = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                related_name='staff')
    full_name = models.CharField(max_length=200)
    email = models.EmailField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    position = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='%(class)s_created')
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='%(class)s_updated')

    class Meta:
        db_table = 'staff'
        indexes = [
            models.Index(fields=['full_name']),
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return self.full_name


class LoginCount(models.Model):
    """Running login counter per user."""

    id = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                related_name='login_count')
    login_count = models.IntegerField(default=0)
    last_login_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='%(class)s_created')
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='%(class)s_updated')

    class Meta:
        db_table = 'login_count'

    def __str__(self):
        return f"{self.user.username}: {self.login_count}"


class Auth(models.Model):
    """Real authentication events: successful logins, failures and logouts."""

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL,
                             blank=True, null=True,
                             related_name='auth_logs')
    username = models.CharField(max_length=150, blank=True, null=True)
    auth_type = models.CharField(max_length=20)
    status = models.CharField(max_length=20, default='success')
    ip_address = models.CharField(max_length=45, blank=True, null=True)
    user_agent = models.CharField(max_length=500, blank=True, null=True)

    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='%(class)s_created')
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='%(class)s_updated')

    class Meta:
        db_table = 'auth'
        indexes = [
            models.Index(fields=['auth_type']),
            models.Index(fields=['status']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(auth_type__in=["LOGIN", "LOGOUT", "FAILED"]),
                name='auth_type_valid',
            ),
            models.CheckConstraint(
                condition=models.Q(status__in=["success", "failure"]),
                name='auth_status_valid',
            ),
        ]

    def __str__(self):
        return f"{self.username} {self.auth_type}"


class CyberIncidents(models.Model):
    """Cybersecurity incident records."""

    incident_id = models.BigIntegerField(primary_key=True)
    timestamp = models.DateTimeField()
    severity = models.CharField(max_length=20, default="Medium")
    category = models.CharField(max_length=50, default="Unknown")
    status = models.CharField(max_length=20, default="Open")
    description = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='%(class)s_created')
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='%(class)s_updated')

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
    created_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='%(class)s_created')
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='%(class)s_updated')

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
    resolution_time_hours = models.IntegerField(blank=True, null=True)

    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='%(class)s_created')
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='%(class)s_updated')

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
    deliberately has no foreign key to ``user``.
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

    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='%(class)s_created')
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='%(class)s_updated')

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

    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='%(class)s_created')
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='%(class)s_updated')

    class Meta:
        db_table = 'analytical_reports'
        indexes = [
            models.Index(fields=['run_id']),
        ]


class AiMonitorState(models.Model):
    """Key/value store for the AI monitor's scan cursor."""

    key = models.CharField(max_length=100, primary_key=True)
    value = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='%(class)s_created')
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='%(class)s_updated')

    class Meta:
        db_table = 'ai_monitor_state'
