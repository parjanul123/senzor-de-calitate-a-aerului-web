from unittest.mock import patch

from django.test import SimpleTestCase
from django.urls import reverse

from apps.measurements.services import MeasurementData


class MeasurementViewsTests(SimpleTestCase):
    @patch("apps.measurements.views.MeasurementService.read_recent")
    def test_history_displays_measurements(self, read_recent):
        read_recent.return_value = MeasurementData(
            columns=["temperature"], latest={"temperature": 24.5}, recent=[{"temperature": 24.5}]
        )

        response = self.client.get(reverse("measurements:history"))

        self.assertContains(response, "Istoric masuratori")
        self.assertContains(response, "24,5")

    @patch("apps.measurements.views.MeasurementService.chart_data")
    def test_chart_data_returns_service_payload(self, chart_data):
        chart_data.return_value = {"labels": ["10:00"], "datasets": {"temperature": [24.5]}}

        response = self.client.get(reverse("measurements:chart_data"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["datasets"]["temperature"], [24.5])