from django.urls import path

from weather_app.views import get_weather

urlpatterns = [
    path('', get_weather, name='base'),
]