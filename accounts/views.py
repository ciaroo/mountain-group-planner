from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from activities.models import Activity, Booking


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
    total_bookings = Booking.objects.filter(
        user=request.user
    ).count()

    context = {
        "total_bookings": total_bookings
    }

    return render(request, "accounts/profile.html", context)