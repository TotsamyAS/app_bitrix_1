from django.urls import path
from its_deal_tutorial_app import views

urlpatterns = [
    path('', views.index, name='index'),
    path('health/', views.health_check, name='health'),  # для проверки работы
]