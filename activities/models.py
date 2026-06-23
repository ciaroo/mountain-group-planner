from django.conf import settings
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Activity(models.Model):
    title = models.CharField(max_length=200)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activities"
    )
    description = models.TextField()
    image = models.ImageField(
        upload_to="activities/",
        blank=True,
        null=True,
        verbose_name="Immagine"
    )
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(blank=True, null=True)
    meeting_place = models.CharField(max_length=200)
    max_participants = models.PositiveIntegerField()
    what_to_bring = models.TextField(blank=True)
    requires_booking = models.BooleanField(
        default=True,
        verbose_name="Richiede prenotazione"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_activities"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Activities"

    @property
    def booked_count(self):
        return self.bookings.count()

    @property
    def available_spots(self):
        if not self.requires_booking:
            return None

        return self.max_participants - self.booked_count

    @property
    def is_full(self):
        if not self.requires_booking:
            return False

        return self.available_spots <= 0

    @property
    def is_almost_full(self):
        if not self.requires_booking:
            return False

        return not self.is_full and self.available_spots <= 3

    def __str__(self):
        return self.title


class Booking(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookings"
    )
    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name="bookings"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "activity")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.activity.title}"


class Notice(models.Model):
    PRIORITY_CHOICES = [
        ("normal", "Normale"),
        ("important", "Importante"),
        ("urgent", "Urgente"),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField()
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default="normal"
    )
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_notices"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title