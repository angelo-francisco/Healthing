from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include("user_auth.urls")),
    path("medicine/", include("medicine.urls")),
    path("", RedirectView.as_view(url="/patient/", permanent=False)),
    path("patient/", include("patient.urls")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
