from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('profile', views.index, name='dashboard.index'),
    path('settings', views.settings, name='dashboard.settings'),
    path('security', views.security, name='dashboard.security'),
    path('ewallet', views.ewallet, name='dashboard.ewallet'),
    path('statements', views.statements, name='dashboard.statements'),
    path('referrals', views.referrals, name='dashboard.referrals'),
    path('logs', views.logs, name='dashboard.logs'),
    path('ledger', views.sports_ledger, name='dashboard.ledger'),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
