"""
URL configuration for work_manage project.
"""
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # The project uses its own custom Employee Management System admin.
    # Django's built-in /admin/ panel is intentionally disabled.
    path("", include("work_manage_app.urls")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
