from django.http import JsonResponse


def error_404(request, exception):
    return JsonResponse({
        "status": "error",
        "data": {
            "message": "We couldn't find this method",
            "code": 404
        }
    }, status=404)


def error_500(request):
    return JsonResponse({
        "status": "error",
        "data": {
            "message": "Internal server error",
            "code": 500
        }
    }, status=500)


def error_400(request, exception):
    return JsonResponse({
        "status": "error",
        "data": {
            "message": "Bad request",
            "code": 400
        }
    }, status=400)
