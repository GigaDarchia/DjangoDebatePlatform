from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Debate

@receiver(post_save, sender=Debate)
def update_user_level(sender, instance, created, **kwargs):
    if not created:
        instance.update_status()