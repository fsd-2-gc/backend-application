import os
from django.http import JsonResponse, HttpResponse
from django.conf import settings


class SimpleCorsMiddleware:
    """
    Minimal CORS middleware to support browser requests from a different origin.

    - Allows all origins by default (or restrict via env CORS_ALLOWED_ORIGINS=origin1,origin2)
    - Handles preflight OPTIONS requests before other middlewares (should be placed first)
    - Adds the appropriate CORS headers to all responses
    """

    def __init__(self, get_response):
        self.get_response = get_response
        allowed = os.getenv("CORS_ALLOWED_ORIGINS")
        self.allowed_origins = (
            [o.strip() for o in allowed.split(",") if o.strip()]
            if allowed
            else None
        )

    def _get_allow_origin(self, origin: str | None):
        if not origin:
            return None
        if self.allowed_origins is None:
            return "*"
        return origin if origin in self.allowed_origins else None

    def __call__(self, request):
        origin = request.headers.get("Origin")
        allow_origin = self._get_allow_origin(origin)

        # Short-circuit preflight with proper CORS headers
        if request.method == "OPTIONS":
            resp = HttpResponse(status=200)
            if allow_origin:
                resp["Access-Control-Allow-Origin"] = allow_origin
                resp["Vary"] = "Origin"
                resp["Access-Control-Allow-Methods"] = "GET, POST, DELETE, OPTIONS"
                resp["Access-Control-Allow-Headers"] = "Content-Type, X-API-Key"
                resp["Access-Control-Max-Age"] = "86400"
            return resp

        response = self.get_response(request)
        if allow_origin:
            response["Access-Control-Allow-Origin"] = allow_origin
            response["Vary"] = "Origin"
        return response


class ApiKeyMiddleware:
    """
    Simple API key gate for the whole app.

    - Expected key is read from env var API_KEY.
    - Accepts credentials via header "X-API-Key" or query param "api_key".
    - Returns JSON 401 on missing/invalid key; JSON 500 if API key is not configured.
    - Catches unhandled exceptions downstream and returns a JSON 500 to ensure API consistency.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Allow unauthenticated CORS preflight requests
        if request.method == "OPTIONS":
            return self.get_response(request)

        expected = os.getenv("API_KEY")
        supplied = request.headers.get("X-API-Key") or request.GET.get("api_key") or ""
        if not supplied or supplied != expected:
            return JsonResponse(
                {
                    "status": "error",
                    "data": {
                        "message": "Invalid API key",
                        "code": 401,
                    },
                },
                status=401,
            )

        # Auth OK — protect against unhandled exceptions to avoid HTML 500s
        try:
            return self.get_response(request)
        except Exception:
            payload = {
                "status": "error",
                "data": {
                    "message": "Internal server error",
                    "code": 500,
                },
            }
            return JsonResponse(payload, status=500)
