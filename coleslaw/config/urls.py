from django.contrib import admin
from django.urls import path, include

from django.conf.urls.static import static
from django.conf import settings

from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('robots.txt',  TemplateView.as_view(template_name="robots.txt", content_type='text/plain')),

    path('system-manage/', include('system_manage.urls')),
    path('shop-manage/', include('shop_manage.urls')),
    path('entry/', include('entry.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
