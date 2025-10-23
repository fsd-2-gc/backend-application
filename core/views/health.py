from django.http import JsonResponse


def health(request):
    return JsonResponse({
        "status": "ok",
        "data": "API is up and running!"
    }, status=200)
