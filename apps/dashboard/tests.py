from unittest.mock import patch

from django.test import SimpleTestCase
from django.urls import reverse

from apps.dashboard.services import MeasurementData


class DashboardTests(SimpleTestCase):
    @patch("apps.dashboard.views.read_measurements")
    def test_dashboard_displays_latest_and_recent_measurements(self, read_measurements):
        read_measurements.return_value = MeasurementData(
            columns=["measured_at", "temperature", "humidity"],
            latest={"measured_at": "2026-08-04 10:00", "temperature": 24.5, "humidity": 55},
            recent=[
                {"measured_at": "2026-08-04 10:00", "temperature": 24.5, "humidity": 55},
                {"measured_at": "2026-08-04 09:59", "temperature": 24.4, "humidity": 56},
            ],
        )

        response = self.client.get(reverse("dashboard:index"))

        self.assertContains(response, "Ultima masuratoare")
        self.assertContains(response, "Ultimele 20 de masuratori")
        self.assertContains(response, "24,5")
        self.assertContains(response, "2026-08-04 09:59")