from django.urls import path

from . import views


app_name = "accounts"


urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path(
        "registration-complete/",
        views.registration_complete,
        name="registration_complete"
    ),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/", views.profile, name="profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("cars/", views.cars_organization, name="cars_organization"),
    path("participants/", views.participant_list, name="participant_list"),
    path("food-summary/", views.food_summary, name="food_summary"),
    path("bookings-overview/", views.bookings_overview, name="bookings_overview"),
    path("export/participants/", views.export_participants_csv, name="export_participants_csv"),
    path("export/bookings/", views.export_bookings_csv, name="export_bookings_csv"),
    path("export/cars/", views.export_cars_csv, name="export_cars_csv"),
]