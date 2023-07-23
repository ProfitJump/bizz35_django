from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='frontend.index'),
    path('<str:ref_code>/', views.index_view, name='frontend.index'),
]
