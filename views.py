from django.shortcuts import render
from .ddio import dd_io
from django.http import HttpResponse

def home(request):
    return render(request, 'home.html')
def about(request):
    return render(request, 'about.html')
def show_projects(request):
    val = dd_io()
    projects = val.io_get_projects()
    context = {"projects": projects}
    return render(request, 'projects.html', context)
def show_sequences(request, project_name):
    val = dd_io(project_name)
    sequences = val.io_get_sequences()
    context = {"project_name": project_name, "sequences": sequences}
    return render(request, 'sequences.html', context)
def show_shots(request, project_name, sequence_name):
    val = dd_io(project_name, sequence_name)
    shots = val.io_get_shots()
    context = {"project_name": project_name, "sequence_name": sequence_name, "shots": shots}
    return render(request, 'shots.html', context)
def show_tasks(request, project_name, sequence_name, shot_name):
    val = dd_io(project_name, sequence_name, shot_name)
    tasks = val.io_get_tasks()
    context = {"shot_name": shot_name ,"project_name": project_name, "sequence_name": sequence_name, "tasks": tasks}
    return render(request, 'tasks.html', context)
def show_users(request):
    val = dd_io()
    users = val.io_get_users()
    context = {"users": users }
    return render(request, 'users.html', context)
