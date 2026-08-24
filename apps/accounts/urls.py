from django.urls import path

from apps.accounts.views import manage_username, profile, set_theme

app_name = "accounts"

urlpatterns = [
    path("", profile, name="profile"),
    path("api/username/", manage_username, name="manage_username"),
    path("api/theme/", set_theme, name="set_theme"),
]