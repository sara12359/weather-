from django.urls import path
from . import views

urlpatterns = [
    path('', views.weather_view, name='weather_view'),
    path('toggle-favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
]
