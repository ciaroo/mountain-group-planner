import csv

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from activities.models import Activity, Booking, Notice

from .forms import ProfileForm, RegistrationForm
from .models import Profile


def register(request):
    if request.user.is_authenticated:
        return redirect("accounts:home")

    if request.method == "POST":
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()

            profile_obj, created = Profile.objects.get_or_create(
                user=user
            )

            profile_obj.display_name = f"{user.first_name} {user.last_name}".strip()
            profile_obj.save()

            login(request, user)

            messages.success(
                request,
                "Registrazione completata. Benvenuto nel sito della vacanza!"
            )

            return redirect("accounts:home")
    else:
        form = RegistrationForm()

    context = {
        "form": form
    }

    return render(request, "registration/register.html", context)


def home(request):
    today = timezone.localdate()

    latest_notice = Notice.objects.filter(
        is_active=True
    ).order_by(
        "-created_at"
    ).first()

    first_future_activity = Activity.objects.filter(
        date__gte=today
    ).order_by(
        "date",
        "start_time"
    ).first()

    first_activity = Activity.objects.all().order_by(
        "date",
        "start_time"
    ).first()

    today_has_activities = Activity.objects.filter(
        date=today
    ).exists()

    if today_has_activities:
        selected_date = today
    elif first_future_activity:
        selected_date = first_future_activity.date
    elif first_activity:
        selected_date = first_activity.date
    else:
        selected_date = None

    if selected_date:
        hero_activities = Activity.objects.filter(
            date=selected_date
        ).order_by(
            "start_time"
        )

        next_today_activity = hero_activities.first()
        hero_activity = hero_activities.first()
    else:
        hero_activities = Activity.objects.none()
        next_today_activity = None
        hero_activity = None

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
        "hero_activities": hero_activities,
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
        has_car=True,
        user__is_superuser=False
    ).select_related("user").order_by(
        "user__first_name",
        "user__last_name",
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


@login_required
def participant_list(request):
    if not request.user.is_staff:
        messages.error(request, "Non hai il permesso per vedere la lista partecipanti.")
        return redirect("accounts:home")

    participants = User.objects.filter(
        is_superuser=False
    ).select_related(
        "profile"
    ).annotate(
        total_bookings=Count("bookings")
    ).order_by(
        "first_name",
        "last_name",
        "username"
    )

    total_participants = participants.count()

    completed_profiles = 0
    participants_with_car = 0
    total_car_seats = 0

    for participant in participants:
        profile_obj = getattr(participant, "profile", None)

        if profile_obj:
            if (
                profile_obj.display_name
                or profile_obj.allergies
                or profile_obj.food_preferences
                or profile_obj.has_car
                or profile_obj.notes
            ):
                completed_profiles += 1

            if profile_obj.has_car:
                participants_with_car += 1
                total_car_seats += profile_obj.car_seats

    context = {
        "participants": participants,
        "total_participants": total_participants,
        "completed_profiles": completed_profiles,
        "participants_with_car": participants_with_car,
        "total_car_seats": total_car_seats,
    }

    return render(request, "accounts/participant_list.html", context)


@login_required
def food_summary(request):
    if not request.user.is_staff:
        messages.error(request, "Non hai il permesso per vedere il riepilogo alimentare.")
        return redirect("accounts:home")

    profiles_with_allergies = Profile.objects.exclude(
        allergies=""
    ).select_related(
        "user"
    ).filter(
        user__is_superuser=False
    ).order_by(
        "user__first_name",
        "user__last_name",
        "user__username"
    )

    profiles_with_preferences = Profile.objects.exclude(
        food_preferences=""
    ).select_related(
        "user"
    ).filter(
        user__is_superuser=False
    ).order_by(
        "user__first_name",
        "user__last_name",
        "user__username"
    )

    profiles_with_notes = Profile.objects.exclude(
        notes=""
    ).select_related(
        "user"
    ).filter(
        user__is_superuser=False
    ).order_by(
        "user__first_name",
        "user__last_name",
        "user__username"
    )

    context = {
        "profiles_with_allergies": profiles_with_allergies,
        "profiles_with_preferences": profiles_with_preferences,
        "profiles_with_notes": profiles_with_notes,
    }

    return render(request, "accounts/food_summary.html", context)


@login_required
def bookings_overview(request):
    if not request.user.is_staff:
        messages.error(request, "Non hai il permesso per vedere il riepilogo prenotazioni.")
        return redirect("accounts:home")

    activities = Activity.objects.filter(
        requires_booking=True
    ).prefetch_related(
        "bookings__user"
    ).order_by(
        "date",
        "start_time"
    )

    context = {
        "activities": activities
    }

    return render(request, "accounts/bookings_overview.html", context)


@login_required
def export_participants_csv(request):
    if not request.user.is_staff:
        messages.error(request, "Non hai il permesso per esportare i partecipanti.")
        return redirect("accounts:home")

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="partecipanti.csv"'

    response.write("\ufeff")

    writer = csv.writer(response)

    writer.writerow([
        "Nome utente",
        "Nome",
        "Cognome",
        "Email",
        "Nome visualizzato",
        "Allergie",
        "Preferenze alimentari",
        "Auto disponibile",
        "Posti auto",
        "Note",
        "Numero prenotazioni",
    ])

    participants = User.objects.filter(
        is_superuser=False
    ).select_related(
        "profile"
    ).annotate(
        total_bookings=Count("bookings")
    ).order_by(
        "first_name",
        "last_name",
        "username"
    )

    for participant in participants:
        profile_obj = getattr(participant, "profile", None)

        if profile_obj:
            display_name = profile_obj.display_name
            allergies = profile_obj.allergies
            food_preferences = profile_obj.food_preferences
            has_car = "Sì" if profile_obj.has_car else "No"
            car_seats = profile_obj.car_seats
            notes = profile_obj.notes
        else:
            display_name = ""
            allergies = ""
            food_preferences = ""
            has_car = "No"
            car_seats = 0
            notes = ""

        writer.writerow([
            participant.username,
            participant.first_name,
            participant.last_name,
            participant.email,
            display_name,
            allergies,
            food_preferences,
            has_car,
            car_seats,
            notes,
            participant.total_bookings,
        ])

    return response


@login_required
def export_bookings_csv(request):
    if not request.user.is_staff:
        messages.error(request, "Non hai il permesso per esportare le prenotazioni.")
        return redirect("accounts:home")

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="prenotazioni.csv"'

    response.write("\ufeff")

    writer = csv.writer(response)

    writer.writerow([
        "Attività",
        "Categoria",
        "Data attività",
        "Ora inizio",
        "Ora fine",
        "Luogo di ritrovo",
        "Partecipante",
        "Username",
        "Email",
        "Data prenotazione",
    ])

    bookings = Booking.objects.select_related(
        "activity",
        "activity__category",
        "user"
    ).filter(
        user__is_superuser=False
    ).order_by(
        "activity__date",
        "activity__start_time",
        "user__first_name",
        "user__last_name",
        "user__username"
    )

    for booking in bookings:
        activity = booking.activity
        user = booking.user

        if activity.category:
            category_name = activity.category.name
        else:
            category_name = ""

        if user.first_name or user.last_name:
            participant_name = f"{user.first_name} {user.last_name}".strip()
        else:
            participant_name = user.username

        if activity.end_time:
            end_time = activity.end_time.strftime("%H:%M")
        else:
            end_time = ""

        writer.writerow([
            activity.title,
            category_name,
            activity.date.strftime("%d/%m/%Y"),
            activity.start_time.strftime("%H:%M"),
            end_time,
            activity.meeting_place,
            participant_name,
            user.username,
            user.email,
            timezone.localtime(booking.created_at).strftime("%d/%m/%Y %H:%M"),
        ])

    return response


@login_required
def export_cars_csv(request):
    if not request.user.is_staff:
        messages.error(request, "Non hai il permesso per esportare l'organizzazione auto.")
        return redirect("accounts:home")

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="auto.csv"'

    response.write("\ufeff")

    writer = csv.writer(response)

    writer.writerow([
        "Partecipante",
        "Username",
        "Email",
        "Modello auto",
        "Posti disponibili",
        "Note",
    ])

    car_profiles = Profile.objects.filter(
        has_car=True,
        user__is_superuser=False
    ).select_related(
        "user"
    ).order_by(
        "user__first_name",
        "user__last_name",
        "user__username"
    )

    for profile in car_profiles:
        user = profile.user

        if profile.display_name:
            participant_name = profile.display_name
        elif user.first_name or user.last_name:
            participant_name = f"{user.first_name} {user.last_name}".strip()
        else:
            participant_name = user.username

        car_model = getattr(profile, "car_model", "")

        writer.writerow([
            participant_name,
            user.username,
            user.email,
            car_model,
            profile.car_seats,
            profile.notes,
        ])

    return response