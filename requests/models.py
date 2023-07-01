from django.utils import timezone

from django.db import models

from account.models import EndUser

from utils.misc import request_image_directory_path


class Request(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField(max_length=510)
    address = models.CharField(max_length=255)
    country = models.CharField(max_length=30)
    city = models.CharField(max_length=30)
    price = models.IntegerField()
    phone_number = models.CharField(max_length=20)
    estimated_profit = models.IntegerField(default=0)
    user = models.ForeignKey(
        EndUser, on_delete=models.CASCADE, related_name="requests"
    )  # User.objects.get(id=1).requests
    image = models.ImageField(upload_to=request_image_directory_path, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_ordered = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk:  # only set on creation
            self.created_at = timezone.localtime(timezone.now())
        super().save(*args, **kwargs)


class Order(models.Model):
    STATUS_CHOICES = [
        (0, "PENDING"),
        (1, "ACCEPTED"),
        (2, "DELIVERED"),
    ]
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    request = models.OneToOneField(
        Request, on_delete=models.CASCADE, related_name="request_order"
    )
    rider = models.OneToOneField(
        EndUser, on_delete=models.CASCADE, related_name="rider_order"
    )
    requestee = models.ForeignKey(
        EndUser, on_delete=models.CASCADE, related_name="user_order"
    )
    score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.STATUS_CHOICES[self.status][1]

    def save(self, *args, **kwargs):
        if not self.pk:  # only set on creation
            self.created_at = timezone.localtime(timezone.now())
        self.updated_at = timezone.localtime(timezone.now())
        super().save(*args, **kwargs)
