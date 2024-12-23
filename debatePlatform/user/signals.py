from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User

@receiver(post_save, sender=User)
def update_user_level(sender, instance, created, **kwargs):
    if not created:
        instance.level_up()