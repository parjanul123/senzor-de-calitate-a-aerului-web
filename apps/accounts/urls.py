from django.urls import path

from apps.accounts.views import profile, manage_username

app_name = "accounts"

urlpatterns = [
    path("", profile, name="profile"),
    path("api/username/", manage_username, name="manage_username"),
]