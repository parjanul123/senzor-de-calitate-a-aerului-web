from django.db import models

# Supabase Auth owns user identities; no Django user model is defined.

class UserProfile(models.Model):
    """Local profile storage for Supabase authenticated users"""
    supabase_user_id = models.CharField(max_length=255, unique=True, primary_key=True)
    username = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'accounts_userprofile'
    
    def __str__(self):
        return f"{self.username} ({self.supabase_user_id[:8]}...)"