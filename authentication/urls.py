from django.urls import path
from . import views

urlpatterns = [
    path('login', views.user_login, name='auth.login'),
    path('register', views.register, name='auth.register'),
    path('logout', views.user_logout, name='auth.logout'),
    path('verify', views.register_verify, name='auth.verify_new_account'),
    path('verify/<session_email>/<code>', views.register_verify, name='auth.verify_new_account'),
]
