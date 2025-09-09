from django.urls import path
from its_deal_tutorial_app import views

urlpatterns = [
    path('', views.index, name='index'),
]