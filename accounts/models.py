from django.conf import settings
from django.db import models


class Profile(models.Model):
    SEX_CHOICES = [
        ("", "---------"),
        ("M", "Maschio"),
        ("F", "Femmina"),
        ("ALTRO", "Altro / preferisco non specificare"),
    ]

    DOCUMENT_TYPE_CHOICES = [
        ("", "---------"),
        ("CI", "Carta d'identità"),
        ("PATENTE", "Patente"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    display_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Nome visualizzato"
    )

    birth_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="Data di nascita"
    )

    birth_place = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Luogo di nascita"
    )

    residence_place = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Luogo di residenza"
    )

    residence_address = models.CharField(
        max_length=250,
        blank=True,
        verbose_name="Via / indirizzo di residenza"
    )


    sex = models.CharField(
        max_length=20,
        choices=SEX_CHOICES,
        blank=True,
        verbose_name="Sesso"
    )

    document_type = models.CharField(
        max_length=20,
        choices=DOCUMENT_TYPE_CHOICES,
        blank=True,
        verbose_name="Tipo di documento"
    )

    document_number = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="Numero documento"
    )

    document_issuing_authority = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Ente rilascio documento"
    )

    wants_linen_rental = models.BooleanField(
        default=False,
        verbose_name="Vuole noleggiare la biancheria"
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
        verbose_name="Ha auto disponibile"
    )

    car_seats = models.PositiveIntegerField(
        default=0,
        verbose_name="Posti auto disponibili"
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Note"
    )

    def __str__(self):
        return f"Profilo di {self.user.username}"