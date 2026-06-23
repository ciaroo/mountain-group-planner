from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "display_name",
        "has_car",
        "car_model",
        "car_seats",
    )
    search_fields = (
        "user__username",
        "display_name",
        "car_model",
        "allergies",
        "food_preferences",
    )
    list_filter = ("has_car",)