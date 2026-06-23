from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ActivityForm
from .models import Activity, Booking, Category


def activity_list(request):
    activities = Activity.objects.all().order_by("date", "start_time")
    categories = Category.objects.all().order_by("name")

    search_query = request.GET.get("q", "")
    selected_category = request.GET.get("category", "")

    if search_query:
        activities = (
            activities.filter(title__icontains=search_query)
            | activities.filter(description__icontains=search_query)
            | activities.filter(meeting_place__icontains=search_query)
        )

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
    activity = get_object_or_404(Activity, pk=pk)

    user_booking = None

    if request.user.is_authenticated:
        user_booking = Booking.objects.filter(
            user=request.user,
            activity=activity
        ).first()

    activity_bookings = Booking.objects.filter(
        activity=activity
    ).select_related("user").order_by("created_at")

    context = {
        "activity": activity,
        "user_booking": user_booking,
        "activity_bookings": activity_bookings,
    }

    return render(request, "activities/activity_detail.html", context)


def book_activity(request, pk):
    activity = get_object_or_404(Activity, pk=pk)

    if not request.user.is_authenticated:
        messages.error(request, "Devi effettuare il login per prenotarti.")
        return redirect("activities:activity_detail", pk=activity.pk)

    if activity.is_full:
        messages.error(request, "Non ci sono più posti disponibili per questa attività.")
        return redirect("activities:activity_detail", pk=activity.pk)

    activity_start = datetime.combine(activity.date, activity.start_time)

    if activity.end_time:
        activity_end = datetime.combine(activity.date, activity.end_time)
    else:
        activity_end = activity_start + timedelta(hours=3)

    user_bookings = Booking.objects.filter(
        user=request.user,
        activity__date=activity.date
    ).select_related("activity")

    conflicting_booking = None

    for booking in user_bookings:
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

        has_conflict = activity_start < booked_end and activity_end > booked_start

        if has_conflict and booked_activity != activity:
            conflicting_booking = booking
            break

    if conflicting_booking:
        messages.error(
            request,
            f"Non puoi prenotarti: sei già impegnato con "
            f"'{conflicting_booking.activity.title}' in quell'orario."
        )
        return redirect("activities:activity_detail", pk=activity.pk)

    booking, created = Booking.objects.get_or_create(
        user=request.user,
        activity=activity
    )

    if created:
        messages.success(request, "Prenotazione effettuata con successo.")
    else:
        messages.warning(request, "Sei già prenotato a questa attività.")

    return redirect("activities:activity_detail", pk=activity.pk)


@login_required
def cancel_booking(request, pk):
    activity = get_object_or_404(Activity, pk=pk)

    booking = Booking.objects.filter(
        user=request.user,
        activity=activity
    ).first()

    if booking:
        booking.delete()
        messages.success(request, "Prenotazione annullata correttamente.")
    else:
        messages.warning(request, "Non avevi una prenotazione per questa attività.")

    return redirect("activities:activity_detail", pk=activity.pk)


@login_required
def my_bookings(request):
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
        form = ActivityForm(request.POST)

        if form.is_valid():
            activity = form.save(commit=False)
            activity.created_by = request.user
            activity.save()
            messages.success(request, "Attività creata correttamente.")
            return redirect("activities:activity_detail", pk=activity.pk)
    else:
        form = ActivityForm()

    context = {
        "form": form
    }

    return render(request, "activities/activity_form.html", context)


@login_required
def update_activity(request, pk):
    activity = get_object_or_404(Activity, pk=pk)

    if not request.user.is_staff:
        messages.error(request, "Non hai il permesso per modificare attività.")
        return redirect("activities:activity_detail", pk=activity.pk)

    if request.method == "POST":
        form = ActivityForm(request.POST, instance=activity)

        if form.is_valid():
            form.save()
            messages.success(request, "Attività modificata correttamente.")
            return redirect("activities:activity_detail", pk=activity.pk)
    else:
        form = ActivityForm(instance=activity)

    context = {
        "form": form,
        "activity": activity
    }

    return render(request, "activities/activity_form.html", context)


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
    activities = Activity.objects.all().order_by("date", "start_time")

    if activities.exists():
        start_date = activities.first().date
    else:
        start_date = None

    calendar_days = []

    if start_date:
        for i in range(8):
            current_date = start_date + timedelta(days=i)

            day_activities = activities.filter(date=current_date)

            calendar_days.append({
                "date": current_date,
                "activities": day_activities
            })

    context = {
        "calendar_days": calendar_days
    }

    return render(request, "activities/activity_calendar.html", context)


def today_program(request):
    first_activity = Activity.objects.all().order_by("date", "start_time").first()

    if first_activity:
        selected_date = first_activity.date
        activities = Activity.objects.filter(
            date=selected_date
        ).order_by("start_time")
    else:
        selected_date = None
        activities = Activity.objects.none()

    user_bookings_today = []

    if request.user.is_authenticated and selected_date:
        user_bookings_today = Booking.objects.filter(
            user=request.user,
            activity__date=selected_date
        ).select_related("activity").order_by(
            "activity__start_time"
        )

    context = {
        "selected_date": selected_date,
        "activities": activities,
        "user_bookings_today": user_bookings_today,
    }

    return render(request, "activities/today.html", context)