import uuid

from django.db import models
from django.db.models import Q


class WebLoginRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "In asteptare"
        APPROVED = "approved", "Aprobat"

    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    user_id = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    approved_at = models.DateTimeField(null=True, blank=True)
    consumed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "web_login_requests"
        indexes = [
            models.Index(
                fields=["token", "status"],
                name="web_login_r_token_84243c_idx",
            )
        ]
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(
                        ("status", "approved"),
                        ("user_id__isnull", False),
                        ("approved_at__isnull", False),
                    )
                    | Q(
                        ("status", "pending"),
                        ("user_id__isnull", True),
                        ("approved_at__isnull", True),
                    )
                ),
                name="web_login_request_status_fields_match",
            )
        ]

    @property
    def is_expired(self):
        from django.utils import timezone

        return self.expires_at <= timezone.now()