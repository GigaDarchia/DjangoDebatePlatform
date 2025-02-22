from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from user.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import transaction

class Category(models.Model):
    name = models.CharField(max_length=30, verbose_name=_("Name"))
    slug = models.SlugField(unique=False, verbose_name=_("Slug"), blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = _("Categories")

    # def save(self, *args, **kwargs):
    #     if not self.slug:
    #         self.slug = slugify(self.name)


class Debate(models.Model):
    STATUS_CHOICES = [
        ("Scheduled", "Scheduled"),
        ("Ongoing", "Ongoing"),
        ("Finished", "Finished"),
        ("Canceled", "Canceled")
    ]
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    description = models.TextField(verbose_name=_("Description"))
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="category_debates",
                                 verbose_name=_("Category"), null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="author_debates", verbose_name=_("Author"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    start_time = models.DateTimeField(verbose_name=_("Start time"))
    end_time = models.DateTimeField(verbose_name=_("End time"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Scheduled", verbose_name=_("Status"))
    participants = models.ManyToManyField(User, related_name="participated_debates", verbose_name=_("Participants"),
                                          blank=True)

    def __str__(self):
        return self.title

    def update_status(self):
        previous_status = self.status

        if timezone.now() < self.start_time:
            self.status = "Scheduled"
        elif self.start_time <= timezone.now() < self.end_time:
            self.status = "Ongoing"
        elif self.end_time <= timezone.now():
            self.status = "Finished"

        if previous_status != self.status:
            self.save()

    def cancel_debate(self):
        self.status = "Canceled"
        self.save()

    def finish_debate(self):
        winner = self.debate_arguments.select_related('author').order_by('-vote_count').first()
        if not winner or winner.vote_count == 0:
            return

        reward_xp = 150

        with transaction.atomic():
            winner.winner = True
            winner.author.xp += reward_xp
            winner.author.wins += 1
            winner.author.save()
            winner.save()


    def clean(self):
        if not self.start_time or not self.end_time:
            raise ValidationError(_("Start time and end time must be set."))

        if self.end_time <= self.start_time:
            raise ValidationError(_("End time must be after start time."))

        elif self.start_time <= timezone.now():
            raise ValidationError(_("Start time must be in the future."))


class Argument(models.Model):
    SIDE_CHOICES = [
        ("Pro", "Pro"),
        ("Con", "Con")
    ]

    text = models.TextField(verbose_name=_("Text"))
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="arguments", verbose_name=_("Author"))
    debate = models.ForeignKey(Debate, on_delete=models.CASCADE, related_name="debate_arguments",
                               verbose_name=_("Debate"))
    vote_count = models.IntegerField(default=0, verbose_name=_("Vote count"))
    side = models.CharField(max_length=3, choices=SIDE_CHOICES, verbose_name=_("Side"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    winner = models.BooleanField(default=False)

    def has_user_voted(self, user):
        self.votes.filter(user=user).exists()

    def __str__(self):
        return self.text[:100]


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_votes", verbose_name=_("User"))
    argument = models.ForeignKey(Argument, on_delete=models.CASCADE, related_name="votes", verbose_name=_("Argument"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))

    def __str__(self):
        return f"{self.user} vote on Argument-{self.argument_id}"

    class Meta:
        unique_together = ("user", "argument")
