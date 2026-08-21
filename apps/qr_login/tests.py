from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import WebLoginRequest


class QRLoginFlowTests(TestCase):
    def test_approved_request_creates_browser_session_once(self):
        self.client.get(reverse("qr_login:start"))
        login_request = WebLoginRequest.objects.get()
        login_request.status = WebLoginRequest.Status.APPROVED
        login_request.user_id = "9b79c55b-99b9-4bd0-a592-4a26c216ab8c"
        login_request.approved_at = timezone.now()
        login_request.save()

        response = self.client.post(reverse("qr_login:complete"), {"token": login_request.token})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["authenticated"])
        login_request.refresh_from_db()
        self.assertIsNotNone(login_request.consumed_at)
        self.assertEqual(self.client.session["supabase_user_id"], str(login_request.user_id))

    def test_expired_request_cannot_be_consumed(self):
        self.client.get(reverse("qr_login:start"))
        login_request = WebLoginRequest.objects.get()
        login_request.status = WebLoginRequest.Status.APPROVED
        login_request.user_id = "9b79c55b-99b9-4bd0-a592-4a26c216ab8c"
        login_request.approved_at = timezone.now()
        login_request.expires_at = timezone.now() - timedelta(seconds=1)
        login_request.save()

        response = self.client.post(reverse("qr_login:complete"), {"token": login_request.token})

        self.assertEqual(response.status_code, 410)