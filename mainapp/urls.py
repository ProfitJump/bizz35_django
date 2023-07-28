# from django.conf.urls import url, include
from django.urls import include, re_path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
                  re_path('admin/', admin.site.urls),
                  re_path('hijack/', include('hijack.urls')),
                  re_path(r'^', include('frontend.urls')),
                  re_path('dashboard/', include('dashboard.urls')),
                  re_path('auth/', include('authentication.urls')),
                  re_path('stripe_api/', include('stripe_api.urls')),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
