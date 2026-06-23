from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from activities.models import Activity, Booking

from .forms import ProfileForm
from .models import Profile


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