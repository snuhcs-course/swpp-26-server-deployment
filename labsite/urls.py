from django.urls import path

from . import views


urlpatterns = [
    path("api/health", views.health, name="health"),
]

handler400 = "labsite.views.bad_request"
handler403 = "labsite.views.forbidden"
handler404 = "labsite.views.not_found"
handler500 = "labsite.views.server_error"
