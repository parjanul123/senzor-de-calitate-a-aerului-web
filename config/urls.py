from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
	path("test-api/", TemplateView.as_view(template_name="test_api_integration.html"), name="test_api"),
	path("", include("apps.dashboard.urls")),
	path("measurements/", include("apps.measurements.urls")),
	path("devices/", include("apps.devices.urls")),
	path("profile/", include("apps.accounts.urls")),
	path("ai/", include("apps.ai.urls")),
	path("qr-login/", include("apps.qr_login.urls")),
]