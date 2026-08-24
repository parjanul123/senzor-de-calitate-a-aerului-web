import time
from ipaddress import ip_address

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse, JsonResponse
from django.utils.deprecation import MiddlewareMixin


def _safe_client_ip(request):
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        candidate = forwarded_for.split(",")[0].strip()
    else:
        candidate = request.META.get("REMOTE_ADDR", "")

    try:
        return str(ip_address(candidate))
    except ValueError:
        return "0.0.0.0"


class SecurityHeadersMiddleware(MiddlewareMixin):
    """Adds hardened security headers, including CSP."""

    def process_response(self, _request, response):
        response["X-Content-Type-Options"] = "nosniff"
        response["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        csp_policy = {
            "default-src": ["'self'"],
            "script-src": ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net"],
            "style-src": ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net"],
            "img-src": ["'self'", "data:", "https:"],
            "connect-src": ["'self'", "https:"],
            "font-src": ["'self'", "data:", "https://cdn.jsdelivr.net"],
            "object-src": ["'none'"],
            "base-uri": ["'self'"],
            "form-action": ["'self'"],
            "frame-ancestors": ["'none'"],
        }

        extra_connect_sources = getattr(settings, "CSP_CONNECT_SRC_EXTRA", [])
        if isinstance(extra_connect_sources, list):
            csp_policy["connect-src"].extend(extra_connect_sources)

        response["Content-Security-Policy"] = "; ".join(
            f"{directive} {' '.join(sources)}"
            for directive, sources in csp_policy.items()
        )

        return response


class RateLimitMiddleware(MiddlewareMixin):
    """Simple per-IP rate limiting for explicitly configured endpoints."""

    def process_request(self, request):
        rules = getattr(settings, "RATE_LIMIT_RULES", {})
        if not rules:
            return None

        path = request.path
        method = request.method.upper()

        for prefix, rule in rules.items():
            if not path.startswith(prefix):
                continue

            methods = rule.get("methods", ["POST"])
            if method not in methods:
                continue

            limit = int(rule.get("limit", 20))
            window = int(rule.get("window", 60))
            ip = _safe_client_ip(request)
            key = f"rl:{prefix}:{method}:{ip}"
            now = int(time.time())

            bucket = cache.get(key)
            if not bucket or now >= bucket.get("reset_at", 0):
                bucket = {"count": 0, "reset_at": now + window}

            bucket["count"] += 1
            cache.set(key, bucket, timeout=window)

            if bucket["count"] > limit:
                retry_after = max(bucket["reset_at"] - now, 1)
                payload = {
                    "success": False,
                    "error": "Too many requests. Please try again shortly.",
                }
                accepts_json = "application/json" in request.headers.get("Accept", "")
                is_api_path = "/api/" in request.path
                is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
                if is_api_path or is_ajax or accepts_json:
                    response = JsonResponse(payload, status=429)
                else:
                    response = HttpResponse(payload["error"], status=429)
                response["Retry-After"] = str(retry_after)
                return response

            return None

        return None