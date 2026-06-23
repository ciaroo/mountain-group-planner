from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("home/", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/", views.profile, name="profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("cars/", views.cars_organization, name="cars_organization"),
]