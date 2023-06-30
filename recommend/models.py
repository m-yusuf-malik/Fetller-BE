from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from account.models import EndUser

# Create your models here.


# class DietPlans(models.Model):
#     pass


class Schedule(models.Model):
    current_day = models.IntegerField(default=1)
    user = models.OneToOneField(
        EndUser, on_delete=models.PROTECT, related_name="schedule"
    )
    critical_day = models.SmallIntegerField(default=0)


class DietPlan(models.Model):
    day = models.SmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(30)]
    )
    time = models.CharField(max_length=20)
    meal = models.TextField(max_length=1028)
    body_type = models.SmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
