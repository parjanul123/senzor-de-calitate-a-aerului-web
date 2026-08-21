from django.urls import path

from . import views

app_name = "qr_login"

urlpatterns = [
    path("", views.start, name="start"),
    path("check-status/", views.check_status, name="check_status"),
    path("complete/", views.complete_login, name="complete"),
    path("logout/", views.logout, name="logout"),
    path("test-approve/", views.test_approve, name="test_approve"),  # DEBUG: Test endpoint
]