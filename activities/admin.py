from django.contrib import admin

from .models import Activity, Booking, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "date",
        "start_time",
        "meeting_place",
        "max_participants",
        "available_spots",
        "created_by",
    )
    list_filter = ("category", "date")
    search_fields = ("title", "description", "meeting_place")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("user", "activity", "created_at")
    list_filter = ("activity", "created_at")
    search_fields = ("user__username", "activity__title")