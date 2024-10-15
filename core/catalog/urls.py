from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('movie/<int:id>/', views.movie_detail, name='movie_detail'),
    path('about/',views.about,name='about')
]