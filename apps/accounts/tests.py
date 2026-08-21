from django.test import RequestFactory, SimpleTestCase

from apps.accounts.views import profile

class ProfileTests(SimpleTestCase):
    def test_profile_displays_qr_session_user(self):
        request = RequestFactory().get("/profile/")
        request.session = {
            "supabase_user_id": "test-user-id",
            "supabase_authenticated_at": "2026-08-04T10:00:00+00:00",
        }

        response = profile(request)

        self.assertContains(response, "test-user-id")