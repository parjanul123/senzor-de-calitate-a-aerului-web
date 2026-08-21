from django.urls import path

from apps.measurements import views

app_name = "measurements"

urlpatterns = [
    path("device/<str:device_id>/", views.history, name="history"),
    path("device/<str:device_id>/charts/", views.charts, name="charts"),
    path("device/<str:device_id>/latest/", views.latest_data, name="latest_data"),
    # Measurement detail pages with zoom
    path("device/<str:device_id>/temperatura/", views.measurement_detail, {"metric": "temperatura"}, name="temperatura"),
    path("device/<str:device_id>/umiditate/", views.measurement_detail, {"metric": "umiditate"}, name="umiditate"),
    path("device/<str:device_id>/presiune/", views.measurement_detail, {"metric": "presiune"}, name="presiune"),
    path("device/<str:device_id>/co2/", views.measurement_detail, {"metric": "co2"}, name="co2"),
    path("device/<str:device_id>/pm1/", views.measurement_detail, {"metric": "pm1"}, name="pm1"),
    path("device/<str:device_id>/pm25/", views.measurement_detail, {"metric": "pm25"}, name="pm25"),
    path("device/<str:device_id>/pm10/", views.measurement_detail, {"metric": "pm10"}, name="pm10"),
    path("device/<str:device_id>/voc/", views.measurement_detail, {"metric": "voc"}, name="voc"),
    path("device/<str:device_id>/lux/", views.measurement_detail, {"metric": "lux"}, name="lux"),
]