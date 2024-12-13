from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.db import models


class User(AbstractUser):
    LEVEL_CHOICES = [
        ("Novice", "Novice"),
        ("Competitor", "Competitor"),
        ("Debater", "Debater"),
        ("Orator", "Orator"),
        ("Rhetorician", "Rhetorician"),
    ]

    first_name = None
    last_name = None
    xp = models.IntegerField(default=0)
    profile_picture = models.ImageField(upload_to="profile_pictures", null=True, blank=True,
                                        verbose_name=_("Profile Picture"))
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default="Novice", verbose_name=_("Level"))
    wins = models.IntegerField(default=0)

    def level_up(self):
        previous_level = self.level

        if self.xp >= 800:
            self.level = "Rhetorician"
        elif self.xp >= 500:
            self.level = "Orator"
        elif self.xp >= 300:
            self.level = "Debater"
        elif self.xp >= 150:
            self.level = "Competitor"
        else:
            self.level = "Novice"

        if self.level != previous_level:
            self.save()

    def __str__(self):
        return self.username
