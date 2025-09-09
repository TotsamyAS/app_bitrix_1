from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('its_deal_tutorial_app.urls')),  # Главная страница
]