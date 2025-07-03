
from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('user/<str:username>/', views.user_page, name='user_page'),
]
