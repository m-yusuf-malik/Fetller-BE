from django.utils import timezone

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from account.models import EndUser


class Schedule(models.Model):
    current_day = models.IntegerField(default=1)
    user = models.OneToOneField(
        EndUser, on_delete=models.PROTECT, related_name="schedule"
    )
    critical_day = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pk:  # only set on creation
            self.created_at =  timezone.localtime(timezone.now())
            self.updated_at =  timezone.localtime(timezone.now())
        super().save(*args, **kwargs)


class DietPlan(models.Model):
    day = models.SmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(30)]
    )
    time = models.CharField(max_length=20)
    meal = models.TextField(max_length=1028)
    body_type = models.SmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
