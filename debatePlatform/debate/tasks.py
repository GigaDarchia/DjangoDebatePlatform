from celery import shared_task
from .models import Debate
from django.db.models import Q


@shared_task(bind=True)
def update_debate_status(self):
    debates = Debate.objects.all()

    for debate in debates.iterator():
        debate.update_status()
        debate.save()

    print("Debate status updated")

