from unittest.mock import patch

from django.test import SimpleTestCase
from django.urls import reverse

from apps.devices.services import DeviceData


class DevicesTests(SimpleTestCase):
    @patch("apps.devices.views.DeviceService.read_devices")
    def test_devices_page_displays_existing_devices(self, read_devices):
        read_devices.return_value = DeviceData(columns=["name"], devices=[{"name": "Senzor birou"}])

        response = self.client.get(reverse("devices:index"))

        self.assertContains(response, "Senzor birou")