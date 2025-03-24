from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomAuthenticationForm

urlpatterns = [
    # Authentication
    path('login/', auth_views.LoginView.as_view(
        template_name='login.html',
        authentication_form=CustomAuthenticationForm
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Dashboard
    path('', views.dashboard_view, name='dashboard'),
    
    # Projects
    path('projects/', views.project_list, name='project_list'),
    path('projects/create/', views.project_create, name='project_create'),
    path('projects/<str:project_name>/', views.project_detail, name='project_detail'),
    path('projects/<str:project_name>/update/', views.project_update, name='project_update'),
    path('projects/<str:project_name>/delete/', views.project_delete, name='project_delete'),
    
    # Sequences (Folders)
    path('projects/<str:project_name>/sequences/', views.sequence_list, name='sequence_list'),
    path('projects/<str:project_name>/sequences/create/', views.sequence_create, name='sequence_create'),
    path('projects/<str:project_name>/sequences/<str:sequence_id>/', views.sequence_detail, name='sequence_detail'),
    path('projects/<str:project_name>/sequences/<str:sequence_id>/update/', views.sequence_update, name='sequence_update'),
    path('projects/<str:project_name>/sequences/<str:sequence_id>/delete/', views.sequence_delete, name='sequence_delete'),
    
    # Shots (Products)
    path('projects/<str:project_name>/shots/', views.shot_list, name='shot_list'),
    path('projects/<str:project_name>/shots/create/', views.shot_create, name='shot_create'),
    path('projects/<str:project_name>/shots/<str:shot_id>/', views.shot_detail, name='shot_detail'),
    path('projects/<str:project_name>/shots/<str:shot_id>/update/', views.shot_update, name='shot_update'),
    path('projects/<str:project_name>/shots/<str:shot_id>/delete/', views.shot_delete, name='shot_delete'),
    
    # Tasks
    path('projects/<str:project_name>/tasks/', views.task_list, name='task_list'),
    path('projects/<str:project_name>/tasks/create/', views.task_create, name='task_create'),
    path('projects/<str:project_name>/tasks/<str:task_id>/', views.task_detail, name='task_detail'),
    path('projects/<str:project_name>/tasks/<str:task_id>/update/', views.task_update, name='task_update'),
    path('projects/<str:project_name>/tasks/<str:task_id>/delete/', views.task_delete, name='task_delete'),
    
    # Shot-specific Tasks
    path('projects/<str:project_name>/shots/<str:shot_id>/tasks/', views.shot_task_list, name='shot_task_list'),
    path('projects/<str:project_name>/shots/<str:shot_id>/tasks/create/', views.shot_task_create, name='shot_task_create'),
]