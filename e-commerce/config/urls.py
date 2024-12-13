from debug_toolbar.toolbar import debug_toolbar_urls
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("health/", lambda request: HttpResponse("OK")),
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/auth/", include("_auth.urls")),
    path("api/", include("core.urls")),
    path("", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("", include("django_prometheus.urls")),
] + debug_toolbar_urls()
