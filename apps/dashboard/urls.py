from django.urls import path

from .views import dashboard, device_dashboard

app_name = "dashboard"

urlpatterns = [
    path("", dashboard, name="index"),
    path("device/<str:device_id>/", device_dashboard, name="device"),
]