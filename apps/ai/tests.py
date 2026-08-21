import json
from unittest.mock import patch

from django.test import RequestFactory, SimpleTestCase
from django.urls import reverse

from apps.ai.views import user_devices


class AIMockEndpointTests(SimpleTestCase):
    def test_train_preserves_selected_device(self):
        response = self.client.post(
            reverse("ai:train"),
            data=json.dumps({"device_id": "sensor-1"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["device_id"], "sensor-1")

    def test_predict_returns_mock_data(self):
        response = self.client.post(
            reverse("ai:predict"),
            data=json.dumps({"device_id": "sensor-1", "temperature": 24}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["mock"])
        self.assertEqual(response.json()["input"]["device_id"], "sensor-1")

    def test_chat_returns_mock_data(self):
        response = self.client.post(
            reverse("ai:chat"),
            data=json.dumps({"message": "Cum este aerul?"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["mock"])
        self.assertIn("reply", response.json())

    def test_anomaly_returns_mock_data(self):
        response = self.client.post(
            reverse("ai:anomaly"),
            data=json.dumps({"device_id": "sensor-1"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["mock"])

    @patch("apps.ai.views.get_service")
    def test_devices_are_filtered_by_authenticated_owner(self, get_service):
        get_service.return_value.get_user_devices.return_value = [
            {"device_id": "sensor-1", "name": "Senzor birou", "owner_id": "user-123"}
        ]
        request = RequestFactory().get(reverse("ai:devices"))
        request.session = {"supabase_user_id": "user-123"}

        response = user_devices(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)["devices"], [{"id": "sensor-1", "name": "Senzor birou"}])
        get_service.return_value.get_user_devices.assert_called_once_with("user-123")