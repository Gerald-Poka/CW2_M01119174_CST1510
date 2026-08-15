import re

import bcrypt
from django.db import models

from cyber.models import (
    Users,
    CyberIncidents,
    DatasetsMetadata,
    ItTickets,
    AuditTrail,
    AnalyticalReports,
    AiMonitorState,
)


# ---------------------------------------------------------------------------
# Password helpers (bcrypt, matches the legacy hashing module)
# ---------------------------------------------------------------------------

def generate_hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(
            password.encode("utf-8"), hashed_password.encode("utf-8")
        )
    except ValueError:
        return False


_PASSWORD_RULES = [
    (lambda p: len(p) >= 8, "Password must be at least 8 characters long."),
    (lambda p: re.search(r"[A-Z]", p), "Password must contain an uppercase letter."),
    (lambda p: re.search(r"[a-z]", p), "Password must contain a lowercase letter."),
    (lambda p: re.search(r"\d", p), "Password must contain a digit."),
    (lambda p: re.search(r"[!@#$%^&*(),.?\":{}|<>]", p),
     "Password must contain a special character."),
]


def validate_password(password: str):
    for check, message in _PASSWORD_RULES:
        if not check(password):
            return False, message
    return True, "OK"


# ---------------------------------------------------------------------------
# User management
# ---------------------------------------------------------------------------

def register_user(username: str, password: str):
    valid, message = validate_password(password)
    if not valid:
        return False, message
    if Users.objects.filter(username=username).exists():
        return False, "Username already exists."
    Users.objects.create(
        username=username,
        password_hash=generate_hash_password(password),
        role="user",
    )
    return True, "User registered successfully."


def get_user(username: str):
    try:
        return Users.objects.get(username=username)
    except Users.DoesNotExist:
        return None


def login_user(username: str, password: str):
    user = get_user(username)
    if user is None:
        return False, "User not found.", None
    if verify_password(password, user.password_hash):
        return True, "Login successful.", user
    return False, "Incorrect password.", None


def change_password(user_id: int, current_password: str, new_password: str):
    try:
        user = Users.objects.get(id=user_id)
    except Users.DoesNotExist:
        return False, "User not found."

    if not verify_password(current_password, user.password_hash):
        return False, "Current password is incorrect."
    if verify_password(new_password, user.password_hash):
        return False, "New password cannot be the same as the current password."

    valid, message = validate_password(new_password)
    if not valid:
        return False, message

    user.password_hash = generate_hash_password(new_password)
    user.save()
    return True, "Password changed successfully."


def admin_change_password(username: str):
    user = get_user(username)
    if user is None:
        return False
    default_password = "password1234"
    user.password_hash = generate_hash_password(default_password)
    user.save()
    return True


def promote_user(username: str):
    user = get_user(username)
    if user is None:
        return False
    user.role = "admin"
    user.save()
    return True


def demote_user(username: str):
    user = get_user(username)
    if user is None:
        return False
    user.role = "user"
    user.save()
    return True


def delete_user(username: str):
    Users.objects.filter(username=username).delete()


def get_all_users():
    return list(Users.objects.all().order_by("id"))


# ---------------------------------------------------------------------------
# Data access (Django ORM over the PostgreSQL database)
# ---------------------------------------------------------------------------

def get_all_cyber_incidents():
    return list(CyberIncidents.objects.all())


def get_all_it_tickets():
    return list(ItTickets.objects.all())


def get_all_datasets_metadata():
    return list(DatasetsMetadata.objects.all())


def add_cyber_incident(timestamp, severity, category, status, description):
    max_id = CyberIncidents.objects.aggregate(m=models.Max("incident_id"))["m"]
    incident_id = 1000 if max_id is None else max_id + 1
    CyberIncidents.objects.create(
        incident_id=incident_id,
        timestamp=timestamp,
        severity=severity,
        category=category,
        status=status,
        description=description,
    )
    return incident_id


def add_metadata(name, rows, columns, uploaded_by, upload_date):
    max_id = DatasetsMetadata.objects.aggregate(m=models.Max("dataset_id"))["m"]
    dataset_id = 1 if max_id is None else max_id + 1
    DatasetsMetadata.objects.create(
        dataset_id=dataset_id,
        name=name,
        rows=rows,
        columns=columns,
        uploaded_by=uploaded_by,
        upload_date=upload_date,
    )
    return dataset_id


def add_it_ticket(priority, description, status, assigned_to, created_at,
                  resolution_time):
    max_id = ItTickets.objects.aggregate(m=models.Max("ticket_id"))["m"]
    ticket_id = 2000 if max_id is None else max_id + 1
    ItTickets.objects.create(
        ticket_id=ticket_id,
        priority=priority,
        description=description,
        status=status,
        assigned_to=assigned_to,
        created_at=created_at,
        resolution_time_hours=_parse_resolution_hours(resolution_time),
    )
    return ticket_id


def _parse_resolution_hours(value):
    """Coerce a resolution-time input into whole hours or None.

    Accepts a bare number ("5"), a number with a unit ("2 hours", "1 day",
    "3 weeks") or an empty/None value. Returns None when unparseable or
    negative, so the CHECK constraint (>= 0 or NULL) always holds.
    """
    if value is None or isinstance(value, (int, float)):
        return None if value is None else int(value)
    text = str(value).strip().lower()
    if not text:
        return None
    match = re.match(r"^(\d+(?:\.\d+)?)\s*(\w*.*)$", text)
    if not match:
        return None
    try:
        hours = float(match.group(1))
    except ValueError:
        return None
    unit = match.group(2)
    if "week" in unit:
        hours *= 168
    elif "day" in unit:
        hours *= 24
    elif "month" in unit:
        hours *= 730
    result = int(round(hours))
    return result if result >= 0 else None


# ---------------------------------------------------------------------------
# Analysis reports + AI monitor state
# ---------------------------------------------------------------------------

def add_analytical_report(run_id, question, answer):
    from django.utils import timezone
    AnalyticalReports.objects.create(
        run_id=run_id,
        question=question,
        answer=answer,
        created_at=timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
    )


def get_reports(run_id=None, limit=None):
    qs = AnalyticalReports.objects.all().order_by("-id")
    if run_id:
        qs = qs.filter(run_id=run_id)
    if limit:
        qs = qs[:limit]
    return list(qs)


def get_report_runs():
    rows = (AnalyticalReports.objects.values_list("run_id", flat=True)
            .order_by("-run_id").distinct())
    return list(rows)


def get_audit_window(after_id=0, limit=100):
    return list(
        AuditTrail.objects.filter(id__gt=after_id).order_by("id")[:limit]
    )


def get_all_audit_trail():
    return list(AuditTrail.objects.all())


def get_state_value(key, default=None):
    try:
        return AiMonitorState.objects.get(key=key).value
    except AiMonitorState.DoesNotExist:
        return default


def set_state_value(key, value):
    AiMonitorState.objects.update_or_create(key=key, defaults={"value": value})
