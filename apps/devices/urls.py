from django.urls import path

from apps.devices.views import devices, update_device_location

app_name = "devices"

urlpatterns = [
    path("", devices, name="index"),
    path("api/update-location/", update_device_location, name="update_location"),
]