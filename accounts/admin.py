from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "display_name",
        "birth_date",
        "birth_place",
        "residence_place",
        "residence_address",
        "sex",
        "document_type",
        "document_issuing_authority",
        "wants_linen_rental",
        "has_car",
        "car_seats",
    ]

    list_filter = [
        "sex",
        "document_type",
        "wants_linen_rental",
        "has_car",
    ]

    search_fields = [
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__email",
        "display_name",
        "birth_place",
        "residence_place",
        "residence_address",
        "document_number",
        "document_issuing_authority",
    ]

    fieldsets = [
        (
            "Utente",
            {
                "fields": [
                    "user",
                    "display_name",
                ]
            },
        ),
        (
            "Dati per registrazione alloggio",
            {
                "fields": [
                    "birth_date",
                    "birth_place",
                    "residence_place",
                    "residence_address",
                    "sex",
                    "document_type",
                    "document_number",
                    "document_issuing_authority",
                    "wants_linen_rental",
                ]
            },
        ),
        (
            "Preferenze personali",
            {
                "fields": [
                    "allergies",
                    "food_preferences",
                    "notes",
                ]
            },
        ),
        (
            "Auto",
            {
                "fields": [
                    "has_car",
                    "car_seats",
                ]
            },
        ),
    ]