from django.urls import path

from . import views

app_name = "activities"

urlpatterns = [
    path("", views.activity_list, name="activity_list"),
    path("today/", views.today_program, name="today_program"),
    path("calendar/", views.activity_calendar, name="activity_calendar"),
    path("notices/", views.notice_list, name="notice_list"),
    path("notices/create/", views.create_notice, name="create_notice"),
    path("notices/<int:pk>/edit/", views.update_notice, name="update_notice"),
    path("notices/<int:pk>/delete/", views.delete_notice, name="delete_notice"),
    path("create/", views.create_activity, name="create_activity"),
    path("my-bookings/", views.my_bookings, name="my_bookings"),
    path("<int:pk>/", views.activity_detail, name="activity_detail"),
    path("<int:pk>/edit/", views.update_activity, name="update_activity"),
    path("<int:pk>/delete/", views.delete_activity, name="delete_activity"),
    path("<int:pk>/book/", views.book_activity, name="book_activity"),
    path("<int:pk>/cancel/", views.cancel_booking, name="cancel_booking"),
]