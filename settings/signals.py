"""
Signals to auto-create default settings for new users
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .utils import ensure_user_default_settings


@receiver(post_save, sender=User)
def create_user_default_settings(sender, instance, created, **kwargs):
    """Automatically create default settings when a new user is created"""
    if created:
        ensure_user_default_settings(instance)

