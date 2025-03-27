from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from projects.views import home, about, projects_ui,tasks_page,update_task, autocomplete_users, folders_page, update_folder, get_projects, update_project ,edit_project, show_projects, add_project, show_sequences, add_sequence,  show_shots, add_shot, show_tasks, add_task, show_users, get_time_data, show_my_tasks, task_detail
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
 path('admin/', admin.site.urls),
 path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
 path('logout/', auth_views.LogoutView.as_view(), name='logout'),
 path('task/<str:task_id>/', task_detail, name='task_detail'),
 path('projects/', show_projects, name = "proj"),
 path('projects/add/', add_project, name='add_project'),
 path('projects/<str:project_id>/edit/', edit_project, name='edit_project'),
 path('users/', show_users, name = "user"),
 path('time-data/', get_time_data, name='time_data'),
 path('my_tasks/', show_my_tasks, name='my_tasks'),
 path('tasks/', tasks_page, name="tasks"),
 path('tasks/<str:project_name>/<str:task_id>/update/', update_task, name='update_task'),
 path('autocomplete/users/', autocomplete_users, name='autocomplete_users'),

 path('folders/', folders_page, name="folders"),
 path('folders/<str:project_name>/<str:folder_id>/update/', update_folder, name='update_folder'),

 path('sequences/<str:project_name>/', show_sequences, name = "seq"),
 path('sequences/<str:project_name>/add/', add_sequence, name="add_sequence"),
 path('shots/<str:project_name>/<str:sequence_name>/', show_shots, name = "shot"),
 path('shots/<str:project_name>/<str:sequence_name>/add/', add_shot, name="add_shot"),
 path('tasks/<str:project_name>/<str:sequence_name>/<str:shot_name>/', show_tasks, name = "task"),
 path('tasks/<str:project_name>/<str:sequence_name>/<str:shot_name>/add', add_task, name = "add_task"),
 path('projects-ui/', projects_ui, name='projects_ui'),
 path('get-projects/', get_projects, name="get_projects"),
 path('update-project/<str:project_name>/', update_project, name="update_project"),
 path('', home),
 path('about/', about),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


