import uuid

from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="WebLoginRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("token", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("status", models.CharField(choices=[("pending", "In asteptare"), ("approved", "Aprobat")], default="pending", max_length=16)),
                ("user_id", models.UUIDField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("expires_at", models.DateTimeField()),
                ("approved_at", models.DateTimeField(blank=True, null=True)),
                ("consumed_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={"db_table": "web_login_requests"},
        ),
        migrations.AddIndex(
            model_name="webloginrequest",
            index=models.Index(fields=["token", "status"], name="web_login_r_token_84243c_idx"),
        ),
        migrations.AddConstraint(
            model_name="webloginrequest",
            constraint=models.CheckConstraint(
                condition=(
                    Q(("status", "approved"), ("user_id__isnull", False), ("approved_at__isnull", False))
                    | Q(("status", "pending"), ("user_id__isnull", True), ("approved_at__isnull", True))
                ),
                name="web_login_request_status_fields_match",
            ),
        ),
    ]