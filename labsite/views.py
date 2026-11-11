import os
import socket

from django.http import JsonResponse


def health(request):
    return JsonResponse(
        {
            "ok": True,
            "worker": os.environ.get("CLASS26_LAB_WORKER", "unset"),
            "hostname": socket.gethostname(),
            "pid": os.getpid(),
        }
    )


def bad_request(request, exception):
    return JsonResponse({"error": "bad_request"}, status=400)


def forbidden(request, exception):
    return JsonResponse({"error": "forbidden"}, status=403)


def not_found(request, exception):
    return JsonResponse({"error": "not_found"}, status=404)


def server_error(request):
    return JsonResponse({"error": "server_error"}, status=500)
