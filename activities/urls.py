from django.urls import path

from . import views

app_name = "activities"

urlpatterns = [
    path("", views.activity_list, name="activity_list"),
    path("create/", views.create_activity, name="create_activity"),
    path("my-bookings/", views.my_bookings, name="my_bookings"),
    path("<int:pk>/", views.activity_detail, name="activity_detail"),
    path("<int:pk>/edit/", views.update_activity, name="update_activity"),
    path("<int:pk>/delete/", views.delete_activity, name="delete_activity"),
    path("<int:pk>/book/", views.book_activity, name="book_activity"),
    path("<int:pk>/cancel/", views.cancel_booking, name="cancel_booking"),
]