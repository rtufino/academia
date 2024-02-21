from django.urls import path
from . import views

urlpatterns = [
    path('homologaciones/', views.homologaciones, name='homologaciones'),
]