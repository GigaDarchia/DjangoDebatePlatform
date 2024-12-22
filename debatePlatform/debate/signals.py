from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Debate

@receiver(pre_save, sender=Debate)
def update_user_level(sender, instance, **kwargs):
    """

    This function listens to the `pre_save` signal of the `Debate` model. It checks
    if the debate's status is transitioning from "Ongoing" to "Finished" and, if
    so, triggers the logic for finalizing the debate.

    """
    if instance.pk:
        old_debate = Debate.objects.get(pk=instance.pk)
        if old_debate.status == "Ongoing" and instance.status == "Finished":
            instance.finish_debate()