from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='user_register'),
    path('register/sent/', views.registration_sent, name='registration_sent'),
    path('register/complete/<str:token>/',views.complete_registration, name='complete_registration'),
]
