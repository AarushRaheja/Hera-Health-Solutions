from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.user_dashboard, name='user_dashboard'),
    path('user/<int:profile_id>/', views.user_page, name='user_page'),
    path('api/assign-files/', views.assign_files, name='assign_files'),
    path('api/upload-files/', views.upload_files, name='upload_files'),
    path('dashboard/files/<str:filename>/', views.serve_file, name='serve_file'),
    path('dashboard/delete-file/<int:profile_id>/<str:filename>/', views.delete_file, name='delete_file'),
]
