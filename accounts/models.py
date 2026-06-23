from django.conf import settings
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    display_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Nome visualizzato"
    )
    allergies = models.TextField(
        blank=True,
        verbose_name="Allergie"
    )
    food_preferences = models.TextField(
        blank=True,
        verbose_name="Preferenze alimentari"
    )
    has_car = models.BooleanField(
        default=False,
        verbose_name="Auto disponibile"
    )
    car_model = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Modello auto"
    )
    car_seats = models.PositiveIntegerField(
        default=0,
        verbose_name="Posti auto disponibili"
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Note personali"
    )

    def __str__(self):
        return f"Profilo di {self.user.username}"