from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import path, include

from utils.views.Misc import MiscAPIView

urlpatterns = [
    path("admin", admin.site.urls),
    path("api/", include("account.urls")),
    path("api/", include("requests.urls")),
    path("api/", include("recommend.urls")),
    path("misc", MiscAPIView.as_view(), name="misc"),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
