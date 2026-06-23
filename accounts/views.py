from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from activities.models import Activity, Booking, Notice

from .forms import ProfileForm
from .models import Profile


def home(request):
    today = timezone.localdate()

    latest_notice = Notice.objects.filter(
        is_active=True
    ).order_by(
        "-created_at"
    ).first()

    hero_activity = Activity.objects.filter(
        requires_booking=False,
        date__gte=today
    ).order_by(
        "date",
        "start_time"
    ).first()

    if hero_activity is None:
        hero_activity = Activity.objects.filter(
            requires_booking=False
        ).order_by(
            "date",
            "start_time"
        ).first()

    first_activity = Activity.objects.all().order_by(
        "date",
        "start_time"
    ).first()

    if first_activity:
        selected_date = first_activity.date
        next_today_activity = Activity.objects.filter(
            date=selected_date
        ).order_by(
            "start_time"
        ).first()
    else:
        selected_date = None
        next_today_activity = None

    next_available_activity = Activity.objects.filter(
        requires_booking=True
    ).order_by(
        "date",
        "start_time"
    ).first()

    next_user_booking = None
    total_bookings = 0
    profile_obj = None
    profile_is_complete = False

    if request.user.is_authenticated:
        next_user_booking = Booking.objects.filter(
            user=request.user
        ).select_related("activity").order_by(
            "activity__date",
            "activity__start_time"
        ).first()

        total_bookings = Booking.objects.filter(
            user=request.user
        ).count()

        profile_obj, created = Profile.objects.get_or_create(
            user=request.user
        )

        profile_is_complete = bool(
            profile_obj.display_name
            and (
                profile_obj.allergies
                or profile_obj.food_preferences
                or profile_obj.has_car
                or profile_obj.notes
            )
        )

    context = {
        "latest_notice": latest_notice,
        "hero_activity": hero_activity,
        "selected_date": selected_date,
        "next_today_activity": next_today_activity,
        "next_available_activity": next_available_activity,
        "next_user_booking": next_user_booking,
        "total_bookings": total_bookings,
        "profile": profile_obj,
        "profile_is_complete": profile_is_complete,
        "total_activities": Activity.objects.count(),
    }

    return render(request, "accounts/home.html", context)


@login_required
def dashboard(request):
    user_bookings = Booking.objects.filter(
        user=request.user
    ).select_related("activity").order_by(
        "activity__date",
        "activity__start_time"
    )

    total_bookings = user_bookings.count()

    context = {
        "user_bookings": user_bookings,
        "total_bookings": total_bookings,
    }

    if request.user.is_staff:
        context["total_activities"] = Activity.objects.count()
        context["total_all_bookings"] = Booking.objects.count()

    return render(request, "accounts/dashboard.html", context)


@login_required
def profile(request):
    profile_obj, created = Profile.objects.get_or_create(
        user=request.user
    )

    total_bookings = Booking.objects.filter(
        user=request.user
    ).count()

    context = {
        "profile": profile_obj,
        "total_bookings": total_bookings,
    }

    return render(request, "accounts/profile.html", context)


@login_required
def edit_profile(request):
    profile_obj, created = Profile.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile_obj)

        if form.is_valid():
            form.save()
            messages.success(request, "Profilo aggiornato correttamente.")
            return redirect("accounts:profile")
    else:
        form = ProfileForm(instance=profile_obj)

    context = {
        "form": form
    }

    return render(request, "accounts/profile_form.html", context)


@login_required
def cars_organization(request):
    if not request.user.is_staff:
        messages.error(request, "Non hai il permesso per vedere l'organizzazione auto.")
        return redirect("accounts:home")

    car_profiles = Profile.objects.filter(
        has_car=True
    ).select_related("user").order_by(
        "user__username"
    )

    total_cars = car_profiles.count()

    total_seats = 0

    for profile in car_profiles:
        total_seats += profile.car_seats

    context = {
        "car_profiles": car_profiles,
        "total_cars": total_cars,
        "total_seats": total_seats,
    }

    return render(request, "accounts/cars.html", context)