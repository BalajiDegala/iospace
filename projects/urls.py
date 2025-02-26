from django.contrib import admin
from django.urls import path
from projects.views import home, about, show_projects, show_sequences, show_shots, show_tasks, show_users

urlpatterns = [
 path('admin/', admin.site.urls),
 path('projects/', show_projects, name = "proj"),
 path('users/', show_users, name = "user"),
 path('sequences/<str:project_name>/', show_sequences, name = "seq"),
 path('shots/<str:project_name>/<str:sequence_name>/', show_shots, name = "shot"),
 path('tasks/<str:project_name>/<str:sequence_name>/<str:shot_name>/', show_tasks, name = "task"),
 path('', home),
 path('about/', about),
]
