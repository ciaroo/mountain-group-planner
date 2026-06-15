from django.shortcuts import get_object_or_404, render

from .models import Activity


def activity_list(request):
    activities = Activity.objects.all().order_by("date", "start_time")

    context = {
        "activities": activities
    }

    return render(request, "activities/activity_list.html", context)


def activity_detail(request, pk):
    activity = get_object_or_404(Activity, pk=pk)

    context = {
        "activity": activity
    }

    return render(request, "activities/activity_detail.html", context)