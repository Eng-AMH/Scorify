from django.conf import settings


def branding(request):
    is_pro = False
    try:
        if request.user.is_authenticated:
            is_pro = bool(getattr(request.user, "profile", None) and request.user.profile.is_pro)
    except Exception:
        is_pro = False

    return {
        "site_url": settings.SITE_URL,
        "site_name": "Scorify",
        "support_email": settings.SUPPORT_EMAIL,
        "user_is_pro": is_pro,
    }
