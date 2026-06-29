from django.conf import settings


def registration_only_mode(request):
    return {
        "registration_only_mode": getattr(settings, "REGISTRATION_ONLY_MODE", False)
    }