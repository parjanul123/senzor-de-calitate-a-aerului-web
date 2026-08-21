from django.urls import path

from apps.devices.views import devices, transport_profile, update_device_location

app_name = "devices"

urlpatterns = [
    path("", devices, name="index"),
    path("<str:device_id>/transport-profile/", transport_profile, name="transport_profile"),
    path("api/update-location/", update_device_location, name="update_location"),
]