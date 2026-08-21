from django.urls import path

from apps.devices.views import devices, transport_profile, transport_profile_data, update_device_location

app_name = "devices"

urlpatterns = [
    path("", devices, name="index"),
    path("<str:device_id>/transport-profile/", transport_profile, name="transport_profile"),
    path("<str:device_id>/transport-profile/data/", transport_profile_data, name="transport_profile_data"),
    path("api/update-location/", update_device_location, name="update_location"),
]