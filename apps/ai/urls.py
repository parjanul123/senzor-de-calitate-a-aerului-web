from django.urls import path

from apps.ai import views

app_name = "ai"

urlpatterns = [
    path("", views.ai_status, name="status"),
    path("interface/", views.ai_interface, name="interface"),
    path("devices/", views.user_devices, name="devices"),
    path("train/", views.train, name="train"),
    path("predict/", views.predict, name="predict"),
    path("anomaly/", views.anomaly, name="anomaly"),
    path("chat/", views.chat, name="chat"),
]