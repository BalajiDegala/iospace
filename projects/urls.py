from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from projects.views import home, about, show_projects, show_sequences, show_shots, show_tasks, show_users, get_time_data, show_my_tasks, task_detail

urlpatterns = [
 path('admin/', admin.site.urls),
 path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
 path('logout/', auth_views.LogoutView.as_view(), name='logout'),
 path('task/<str:task_id>/', task_detail, name='task_detail'),
 path('projects/', show_projects, name = "proj"),
 path('users/', show_users, name = "user"),
 path('time-data/', get_time_data, name='time_data'),
 path('my_tasks/', show_my_tasks, name='my_tasks'),
 path('sequences/<str:project_name>/', show_sequences, name = "seq"),
 path('shots/<str:project_name>/<str:sequence_name>/', show_shots, name = "shot"),
 path('tasks/<str:project_name>/<str:sequence_name>/<str:shot_name>/', show_tasks, name = "task"),
 path('', home),
 path('about/', about),
]


