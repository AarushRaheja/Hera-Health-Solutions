from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.user_dashboard, name='user_dashboard'),
    path('profile/', views.user_profile, name='user_profile'),
    path('user/<int:user_id>/', views.user_page, name='user_page'),
    path('api/assign-files/', views.assign_files, name='assign_files'),
    path('api/upload-files/', views.upload_files, name='upload_files'),
    path('dashboard/files/<str:filename>/', views.serve_file, name='serve_file'),
    path('dashboard/delete/<str:filename>/', views.delete_file, name='delete_file'),
    path('dashboard/delete-assigned/<int:user_id>/<str:filename>/', views.delete_assigned_file, name='delete_assigned_file'),
    path('api/upload-user-file/', views.upload_user_file, name='upload_user_file'),
]
