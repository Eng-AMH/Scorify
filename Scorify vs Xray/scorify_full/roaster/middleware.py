"""
DBRateLimitMiddleware
─────────────────────
DB-based rate limiter for anonymous uploads.
Survives worker restarts unlike the old in-memory version.
Runs a lightweight cleanup every ~100 requests to keep the table small.
"""
import random
from django.conf import settings
from django.http import JsonResponse


def _get_ip(request) -> str:
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    return xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR', '0.0.0.0')


class DBRateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response  = get_response
        self.limit  = getattr(settings, 'UPLOAD_RATE_LIMIT_ANON', 5)
        self.window = getattr(settings, 'UPLOAD_RATE_LIMIT_WINDOW', 3600)

    def __call__(self, request):
        if (request.path == '/api/upload/'
                and request.method == 'POST'
                and not request.user.is_authenticated):
            from .models import RateLimitRecord
            ip = _get_ip(request)
            if RateLimitRecord.count(ip, self.window) >= self.limit:
                return JsonResponse({
                    'error':   'rate_limited',
                    'message': 'Too many requests. Sign up for a free account to get more uploads.',
                }, status=429)
            RateLimitRecord.add(ip)
            # Probabilistic cleanup ~1% of requests — keeps table lean
            if random.random() < 0.01:
                RateLimitRecord.cleanup()

        return self.get_response(request)
