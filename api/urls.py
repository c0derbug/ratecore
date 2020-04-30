from django.urls import include, path
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from gandhi import settings

from . import v1

urlpatterns = [
    # API version 1
    path('v1/', include(v1.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
