from datetime import datetime, timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ActivityForm, NoticeForm
from .models import Activity, Booking, Category, Notice


def registration_only_redirect(request):
    registration_only_mode = getattr(settings, "REGISTRATION_ONLY_MODE", False)

    if not registration_only_mode:
        return None

    if request.user.is_authenticated and request.user.is_staff:
        return None

    if request.user.is_authenticated:
        return redirect("accounts:registration_complete")

    return redirect("accounts:register")


def activity_list(request):
    restricted_redirect = registration_only_redirect(request)

    if restricted_redirect:
        return restricted_redirect

    activities = Activity.objects.filter(
        requires_booking=True
    ).order_by(
        "date",
        "start_time"
    )

    categories = Category.objects.all().order_by("name")

    search_query = request.GET.get("q", "")
    selected_category = request.GET.get("category", "")

    if search_query:
        activities = (
            activities.filter(title__icontains=search_query)
            | activities.filter(description__icontains=search_query)
            | activities.filter(meeting_place__icontains=search_query)
        ).distinct().order_by("date", "start_time")

    if selected_category:
        activities = activities.filter(category_id=selected_category)

    context = {
        "activities": activities,
        "categories": categories,
        "search_query": search_query,
        "selected_category": selected_category,
    }

    return render(request, "activities/activity_list.html", context)


def activity_detail(request, pk):
    restricted_redirect = registration_only_redirect(request)

    if restricted_redirect:
        return restricted_redirect

    activity = get_object_or_404(Activity, pk=pk)

    user_booking = None

    if request.user.is_authenticated:
        user_booking = Booking.objects.filter(
            user=request.user,
            activity=activity
        ).first()

    activity_bookings = Booking.objects.filter(
        activity=activity
    ).select_related("user").order_by("user__username")

    context = {
        "activity": activity,
        "user_booking": user_booking,
        "activity_bookings": activity_bookings,
    }

    return render(request, "activities/activity_detail.html", context)


@login_required
def book_activity(request, pk):
    restricted_redirect = registration_only_redirect(request)

    if restricted_redirect:
        return restricted_redirect

    with transaction.atomic():
        activity = get_object_or_404(
            Activity.objects.select_for_update(),
            pk=pk
        )

        if not activity.requires_booking:
            messages.error(
                request,
                "Questa è un'attività di gruppo: non è necessaria la prenotazione."
            )
            return redirect("activities:activity_detail", pk=activity.pk)

        existing_booking = Booking.objects.filter(
            user=request.user,
            activity=activity
        ).first()

        if existing_booking:
            messages.info(request, "Sei già prenotato a questa attività.")
            return redirect("activities:activity_detail", pk=activity.pk)

        if activity.is_full:
            messages.error(request, "Questa attività è già al completo.")
            return redirect("activities:activity_detail", pk=activity.pk)

        activity_start = datetime.combine(activity.date, activity.start_time)

        if activity.end_time:
            activity_end = datetime.combine(activity.date, activity.end_time)
        else:
            activity_end = activity_start + timedelta(hours=3)

        user_bookings_same_day = Booking.objects.filter(
            user=request.user,
            activity__date=activity.date
        ).select_related("activity")

        for booking in user_bookings_same_day:
            booked_activity = booking.activity

            booked_start = datetime.combine(
                booked_activity.date,
                booked_activity.start_time
            )

            if booked_activity.end_time:
                booked_end = datetime.combine(
                    booked_activity.date,
                    booked_activity.end_time
                )
            else:
                booked_end = booked_start + timedelta(hours=3)

            activities_overlap = activity_start < booked_end and activity_end > booked_start

            if activities_overlap:
                messages.error(
                    request,
                    "Non puoi prenotarti: hai già un'altra attività nello stesso orario."
                )
                return redirect("activities:activity_detail", pk=activity.pk)

        Booking.objects.create(
            user=request.user,
            activity=activity
        )

    messages.success(request, "Prenotazione effettuata correttamente.")
    return redirect("activities:activity_detail", pk=activity.pk)


@login_required
def cancel_booking(request, pk):
    restricted_redirect = registration_only_redirect(request)

    if restricted_redirect:
        return restricted_redirect

    activity = get_object_or_404(Activity, pk=pk)

    booking = Booking.objects.filter(
        user=request.user,
        activity=activity
    ).first()

    if booking:
        booking.delete()
        messages.success(request, "Prenotazione annullata correttamente.")
    else:
        messages.info(request, "Non eri prenotato a questa attività.")

    return redirect("activities:activity_detail", pk=activity.pk)


@login_required
def my_bookings(request):
    restricted_redirect = registration_only_redirect(request)

    if restricted_redirect:
        return restricted_redirect

    bookings = Booking.objects.filter(
        user=request.user
    ).select_related("activity").order_by(
        "activity__date",
        "activity__start_time"
    )

    context = {
        "bookings": bookings
    }

    return render(request, "activities/my_bookings.html", context)


@login_required
def create_activity(request):
    if not request.user.is_staff:
        messages.error(request, "Non hai il permesso per creare attività.")
        return redirect("activities:activity_list")

    if request.method == "POST":
        form = ActivityForm(request.POST, request.FILES)

        if form.is_valid():
            activity = form.save(commit=False)
            activity.created_by = request.user
            activity.save()
            messages.success(request, "Attività creata correttamente.")
            return redirect("activities:activity_detail", pk=activity.pk)
    else:
        form = ActivityForm()

    context = {
        "form": form,
        "title": "Crea attività",
    }

    return render(request, "activities/activity_form.html", context)


@login_required
def update_activity(request, pk):
    activity = get_object_or_404(Activity, pk=pk)

    if not request.user.is_staff:
        messages.error(request, "Non hai il permesso per modificare attività.")
        return redirect("activities:activity_detail", pk=activity.pk)

    if request.method == "POST":
        form = ActivityForm(request.POST, request.FILES, instance=activity)

        if form.is_valid():
            form.save()
            messages.success(request, "Attività aggiornata correttamente.")
            return redirect("activities:activity_detail", pk=activity.pk)
    else:
        form = ActivityForm(instance=activity)

    context = {
        "form": form,
        "title": "Modifica attività",
        "activity": activity,
    }

    return render(request, "activities/activity_form.html", context)


@login_required
def duplicate_activity(request, pk):
    activity = get_object_or_404(Activity, pk=pk)

    if not request.user.is_staff:
        messages.error(request, "Non hai il permesso per duplicare attività.")
        return redirect("activities:activity_detail", pk=activity.pk)

    if request.method == "POST":
        raw_dates = request.POST.get("dates", "")
        date_lines = raw_dates.splitlines()

        valid_dates = []
        invalid_dates = []

        for line in date_lines:
            clean_line = line.strip()

            if not clean_line:
                continue

            try:
                parsed_date = datetime.strptime(clean_line, "%Y-%m-%d").date()
                valid_dates.append(parsed_date)
            except ValueError:
                invalid_dates.append(clean_line)

        if invalid_dates:
            messages.error(
                request,
                "Alcune date non sono valide. Usa il formato AAAA-MM-GG, una data per riga."
            )

            context = {
                "activity": activity,
                "dates": raw_dates,
                "invalid_dates": invalid_dates,
            }

            return render(request, "activities/duplicate_activity.html", context)

        if not valid_dates:
            messages.error(request, "Inserisci almeno una data valida.")

            context = {
                "activity": activity,
                "dates": raw_dates,
            }

            return render(request, "activities/duplicate_activity.html", context)

        created_count = 0

        for new_date in valid_dates:
            Activity.objects.create(
                title=activity.title,
                category=activity.category,
                description=activity.description,
                image=activity.image,
                date=new_date,
                start_time=activity.start_time,
                end_time=activity.end_time,
                meeting_place=activity.meeting_place,
                max_participants=activity.max_participants,
                price=activity.price,
                what_to_bring=activity.what_to_bring,
                requires_booking=activity.requires_booking,
                created_by=request.user,
            )

            created_count += 1

        messages.success(
            request,
            f"Attività duplicata correttamente per {created_count} giorno/i."
        )

        return redirect("activities:activity_detail", pk=activity.pk)

    context = {
        "activity": activity,
        "dates": "",
    }

    return render(request, "activities/duplicate_activity.html", context)


@login_required
def delete_activity(request, pk):
    activity = get_object_or_404(Activity, pk=pk)

    if not request.user.is_staff:
        messages.error(request, "Non hai il permesso per eliminare attività.")
        return redirect("activities:activity_detail", pk=activity.pk)

    if request.method == "POST":
        activity.delete()
        messages.success(request, "Attività eliminata correttamente.")
        return redirect("activities:activity_list")

    context = {
        "activity": activity
    }

    return render(request, "activities/activity_confirm_delete.html", context)


def activity_calendar(request):
    restricted_redirect = registration_only_redirect(request)

    if restricted_redirect:
        return restricted_redirect

    activities = Activity.objects.all().order_by(
        "date",
        "start_time"
    )

    activities_by_date = {}

    for activity in activities:
        activity_start = datetime.combine(
            activity.date,
            activity.start_time
        )

        if activity.end_time:
            activity_end = datetime.combine(
                activity.date,
                activity.end_time
            )
        else:
            activity_end = activity_start + timedelta(hours=3)

        duration_minutes = int(
            (activity_end - activity_start).total_seconds() / 60
        )

        activity.duration_minutes = duration_minutes

        if duration_minutes <= 120:
            activity.duration_class = "duration-short"
        elif duration_minutes <= 240:
            activity.duration_class = "duration-medium"
        else:
            activity.duration_class = "duration-long"

        if activity.date not in activities_by_date:
            activities_by_date[activity.date] = []

        activities_by_date[activity.date].append(activity)

    context = {
        "activities_by_date": activities_by_date
    }

    return render(request, "activities/activity_calendar.html", context)

def today_program(request):
    restricted_redirect = registration_only_redirect(request)

    if restricted_redirect:
        return restricted_redirect

    first_activity = Activity.objects.all().order_by(
        "date",
        "start_time"
    ).first()

    if first_activity:
        selected_date = first_activity.date
        activities = Activity.objects.filter(
            date=selected_date
        ).order_by(
            "start_time"
        )
    else:
        selected_date = None
        activities = Activity.objects.none()

    context = {
        "selected_date": selected_date,
        "activities": activities,
    }

    return render(request, "activities/today.html", context)


def notice_list(request):
    restricted_redirect = registration_only_redirect(request)

    if restricted_redirect:
        return restricted_redirect

    if request.user.is_authenticated and request.user.is_staff:
        notices = Notice.objects.all()
    else:
        notices = Notice.objects.filter(is_active=True)

    context = {
        "notices": notices
    }

    return render(request, "activities/notice_list.html", context)


@login_required
def create_notice(request):
    if not request.user.is_staff:
        messages.error(request, "Non hai il permesso per creare avvisi.")
        return redirect("activities:notice_list")

    if request.method == "POST":
        form = NoticeForm(request.POST)

        if form.is_valid():
            notice = form.save(commit=False)
            notice.created_by = request.user
            notice.save()
            messages.success(request, "Avviso creato correttamente.")
            return redirect("activities:notice_list")
    else:
        form = NoticeForm()

    context = {
        "form": form,
        "title": "Crea avviso",
    }

    return render(request, "activities/notice_form.html", context)


@login_required
def update_notice(request, pk):
    notice = get_object_or_404(Notice, pk=pk)

    if not request.user.is_staff:
        messages.error(request, "Non hai il permesso per modificare avvisi.")
        return redirect("activities:notice_list")

    if request.method == "POST":
        form = NoticeForm(request.POST, instance=notice)

        if form.is_valid():
            form.save()
            messages.success(request, "Avviso aggiornato correttamente.")
            return redirect("activities:notice_list")
    else:
        form = NoticeForm(instance=notice)

    context = {
        "form": form,
        "title": "Modifica avviso",
        "notice": notice,
    }

    return render(request, "activities/notice_form.html", context)


@login_required
def delete_notice(request, pk):
    notice = get_object_or_404(Notice, pk=pk)

    if not request.user.is_staff:
        messages.error(request, "Non hai il permesso per eliminare avvisi.")
        return redirect("activities:notice_list")

    if request.method == "POST":
        notice.delete()
        messages.success(request, "Avviso eliminato correttamente.")
        return redirect("activities:notice_list")

    context = {
        "notice": notice
    }

    return render(request, "activities/notice_confirm_delete.html", context)