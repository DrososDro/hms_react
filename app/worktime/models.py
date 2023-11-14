"""Models for the worktime app"""
import uuid
from django.contrib.auth import get_user_model
from django.db import models


# Create your models here.
class Shift(models.Model):
    """Here we have the shift model
    The shift is the time that the sift starts and ends"""

    id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        primary_key=True,
        editable=False,
    )

    start_of_shift = models.TimeField()
    end_of_shift = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.start_of_shift}-{self.end_of_shift}"


class WorkDay(models.Model):
    """This model is one work day"""

    VOTES = [
        (0, "Normal"),
        (1, "Weekend"),
        (2, "Times off"),
        (3, "Sick leave"),
        (4, "Public holiday"),
        (5, "Job Travel"),
    ]

    id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        primary_key=True,
        editable=False,
    )

    day = models.IntegerField(choices=VOTES, default="0")
    start_of_work = models.TimeField(null=True)
    end_of_work = models.TimeField(null=True)
    date = models.DateField()
    created = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(max_length=200, null=True, blank=True)
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)

    class Meta:
        ordering = ["date"]

    def __str__(self) -> str:
        return str(self.date)
