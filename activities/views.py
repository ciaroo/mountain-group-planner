from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import Activity, Booking
from .forms import ActivityForm


def activity_list(request):
    activities = Activity.objects.all().order_by("date", "start_time")

    context = {
        "activities": activities
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

    context = {
        "activity": activity,
        "user_booking": user_booking
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